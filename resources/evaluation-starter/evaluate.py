"""
Evaluation runner for Persona Weave personas.

Sends test prompts to a persona via Ollama, then uses a second LLM
call (LLM-as-judge) to score each response on four qualitative
dimensions.  Results are printed as a summary table and saved to JSON.

Usage:
    python evaluate.py --verbose                  # Evaluate all personas
    python evaluate.py --persona tutor --verbose  # Evaluate one persona
    python evaluate.py --persona tutor --category emotional
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from ollama import chat

from rubrics import ALL_DIMENSIONS, format_rubric_for_llm
from metrics import summary_stats


# ── Constants ─────────────────────────────────────────────────

DEFAULT_MODEL = "llama3.1"
JUDGE_MODEL = "llama3.1"
PERSONAS_DIR = "personas"
PROMPTS_FILE = "test_prompts.json"
RESULTS_DIR = "results"


# ── Persona loading ───────────────────────────────────────────

def load_persona(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_all_personas(directory: str = PERSONAS_DIR) -> dict[str, dict]:
    personas = {}
    for p in sorted(Path(directory).glob("*.yaml")):
        data = load_persona(str(p))
        personas[p.stem] = data
    return personas


# ── Prompt loading ────────────────────────────────────────────

def load_prompts(
    path: str = PROMPTS_FILE,
    category: str | None = None,
    persona: str | None = None,
) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    prompts = data["prompts"]

    if category:
        prompts = [p for p in prompts if p["category"] == category]

    if persona:
        prompts = [p for p in prompts
                   if not p.get("target_personas")
                   or persona in p["target_personas"]]

    return prompts


# ── Response collection ───────────────────────────────────────

def collect_response(
    persona: dict,
    prompt_text: str,
    model: str = DEFAULT_MODEL,
) -> dict:
    """Send a single prompt to the persona and collect the response."""
    messages = [
        {"role": "system", "content": persona.get("system_prompt", "")},
        {"role": "user", "content": prompt_text},
    ]

    temperature = persona.get("temperature", 0.7)

    start = time.time()
    response = chat(
        model=model,
        messages=messages,
        options={"temperature": temperature},
    )
    elapsed_ms = (time.time() - start) * 1000

    content = response["message"]["content"]

    return {
        "prompt": prompt_text,
        "response": content,
        "response_time_ms": round(elapsed_ms, 1),
        "model": model,
        "persona_name": persona.get("name", "Unknown"),
    }


# ── LLM-as-judge scoring ─────────────────────────────────────

JUDGE_SYSTEM_PROMPT = (
    "You are an impartial evaluator assessing AI persona responses. "
    "You will be given a persona definition, a user prompt, and the "
    "persona's response. Score the response on each dimension using "
    "the rubric provided. Be critical but fair."
)


def build_judge_prompt(persona: dict, prompt_text: str, response_text: str) -> str:
    persona_desc = (
        f"Persona: {persona.get('name', 'Unknown')}\n"
        f"Bio: {persona.get('bio', '')}\n"
        f"Traits: {', '.join(persona.get('traits', []))}\n"
        f"Expertise: {', '.join(persona.get('expertise', []))}\n"
    )

    rubric_text = format_rubric_for_llm()

    return (
        f"## Persona Definition\n{persona_desc}\n"
        f"## User Prompt\n{prompt_text}\n\n"
        f"## Persona Response\n{response_text}\n\n"
        f"## Evaluation Rubric\n{rubric_text}\n"
        f"## Instructions\n"
        f"Score the response on each dimension (1-5). "
        f"Return your answer as a JSON object with this exact format:\n"
        f'{{"scores": {{"psychological_depth": <int>, "emotional_realism": <int>, '
        f'"narrative_coherence": <int>, "human_likeness": <int>}}, '
        f'"justifications": {{"psychological_depth": "<brief reason>", '
        f'"emotional_realism": "<brief reason>", '
        f'"narrative_coherence": "<brief reason>", '
        f'"human_likeness": "<brief reason>"}}}}\n\n'
        f"Return ONLY the JSON object, no other text."
    )


def parse_judge_response(text: str) -> dict:
    """Extract scores JSON from judge response, with fallbacks."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding any JSON object in the text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Return default scores if all parsing fails
    return {
        "scores": {dim.name: 0 for dim in ALL_DIMENSIONS},
        "justifications": {dim.name: "Failed to parse judge response" for dim in ALL_DIMENSIONS},
        "parse_error": True,
    }


def judge_response(
    persona: dict,
    prompt_text: str,
    response_text: str,
    model: str = JUDGE_MODEL,
) -> dict:
    """Use an LLM to score a persona response on rubric dimensions."""
    judge_prompt = build_judge_prompt(persona, prompt_text, response_text)

    messages = [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": judge_prompt},
    ]

    response = chat(
        model=model,
        messages=messages,
        options={"temperature": 0.1},
    )

    result = parse_judge_response(response["message"]["content"])

    scores = result.get("scores", {})
    for dim in ALL_DIMENSIONS:
        if dim.name not in scores:
            scores[dim.name] = 0
        scores[dim.name] = max(1, min(5, int(scores[dim.name]))) if scores[dim.name] else 0

    return {
        "scores": scores,
        "justifications": result.get("justifications", {}),
        "judge_model": model,
        "parse_error": result.get("parse_error", False),
    }


# ── Consistency checking ──────────────────────────────────────

def find_consistency_pairs(prompts: list[dict]) -> list[tuple[dict, dict]]:
    """Find paired consistency-check prompts by ID pattern."""
    consistency = [p for p in prompts if p["category"] == "consistency"]
    pairs = {}
    for p in consistency:
        base_id = re.sub(r"[ab]$", "", p["id"])
        pairs.setdefault(base_id, []).append(p)

    return [(group[0], group[1])
            for group in pairs.values()
            if len(group) >= 2]


def check_consistency(
    persona: dict,
    prompt_a: str,
    prompt_b: str,
    model: str = DEFAULT_MODEL,
) -> dict:
    """Send two related prompts independently and judge consistency."""
    resp_a = collect_response(persona, prompt_a, model)
    resp_b = collect_response(persona, prompt_b, model)

    judge_prompt = (
        f"Two prompts were sent independently to the same persona.\n\n"
        f"Prompt A: {prompt_a}\nResponse A: {resp_a['response']}\n\n"
        f"Prompt B: {prompt_b}\nResponse B: {resp_b['response']}\n\n"
        f"Rate the consistency between these two responses on a 1-5 scale:\n"
        f"  1 = Completely contradictory\n"
        f"  3 = Somewhat consistent but with notable differences\n"
        f"  5 = Highly consistent, same core message and personality\n\n"
        f'Return ONLY a JSON object: {{"consistency_score": <int>, "explanation": "<brief>"}}'
    )

    messages = [
        {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
        {"role": "user", "content": judge_prompt},
    ]

    response = chat(model=model, messages=messages, options={"temperature": 0.1})
    parsed = parse_judge_response(response["message"]["content"])

    return {
        "prompt_a": prompt_a,
        "prompt_b": prompt_b,
        "response_a": resp_a["response"],
        "response_b": resp_b["response"],
        "consistency_score": parsed.get("consistency_score",
                                        parsed.get("scores", {}).get("consistency_score", 0)),
        "explanation": parsed.get("explanation", ""),
    }


# ── Full evaluation pipeline ─────────────────────────────────

def run_evaluation(
    persona_id: str,
    model: str = DEFAULT_MODEL,
    judge_model: str = JUDGE_MODEL,
    category: str | None = None,
    verbose: bool = False,
) -> dict:
    """Run the full evaluation pipeline for a single persona."""
    personas = load_all_personas()
    if persona_id not in personas:
        print(f"Error: Persona '{persona_id}' not found. Available: {list(personas.keys())}")
        sys.exit(1)

    persona = personas[persona_id]
    prompts = load_prompts(category=category, persona=persona_id)

    # Separate consistency prompts from regular prompts
    consistency_pairs = find_consistency_pairs(prompts)
    consistency_ids = set()
    for a, b in consistency_pairs:
        consistency_ids.add(a["id"])
        consistency_ids.add(b["id"])

    regular_prompts = [p for p in prompts if p["id"] not in consistency_ids]

    print(f"\nEvaluating: {persona.get('name', persona_id)} ({model})")
    print(f"Prompts: {len(regular_prompts)} regular + {len(consistency_pairs)} consistency pairs")
    print("-" * 60)

    # Evaluate regular prompts
    results = []
    for i, prompt in enumerate(regular_prompts):
        if verbose:
            print(f"  [{i+1}/{len(regular_prompts)}] {prompt['category']}: "
                  f"{prompt['text'][:50]}...")

        resp = collect_response(persona, prompt["text"], model)
        scores = judge_response(persona, prompt["text"], resp["response"], judge_model)

        results.append({
            "prompt_id": prompt["id"],
            "category": prompt["category"],
            "prompt_text": prompt["text"],
            "response": resp["response"],
            "response_time_ms": resp["response_time_ms"],
            "scores": scores["scores"],
            "justifications": scores["justifications"],
            "parse_error": scores.get("parse_error", False),
        })

    # Evaluate consistency pairs
    consistency_results = []
    for i, (pa, pb) in enumerate(consistency_pairs):
        if verbose:
            print(f"  [consistency {i+1}/{len(consistency_pairs)}] "
                  f"{pa['text'][:40]}...")

        result = check_consistency(persona, pa["text"], pb["text"], model)
        consistency_results.append({
            "pair_ids": [pa["id"], pb["id"]],
            **result,
        })

    # Aggregate scores
    dim_scores: dict[str, list[float]] = {dim.name: [] for dim in ALL_DIMENSIONS}
    response_times = []

    for r in results:
        response_times.append(r["response_time_ms"])
        for dim in ALL_DIMENSIONS:
            score = r["scores"].get(dim.name, 0)
            if score > 0:
                dim_scores[dim.name].append(score)

    consistency_scores = [c["consistency_score"] for c in consistency_results
                          if c["consistency_score"] > 0]

    evaluation = {
        "persona_id": persona_id,
        "persona_name": persona.get("name", persona_id),
        "model": model,
        "judge_model": judge_model,
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "consistency_results": consistency_results,
        "summary": {
            dim.name: summary_stats(dim_scores[dim.name])
            for dim in ALL_DIMENSIONS
        },
        "consistency_summary": summary_stats(consistency_scores),
        "response_time_summary": summary_stats(response_times),
        "total_prompts": len(regular_prompts),
        "total_consistency_pairs": len(consistency_pairs),
        "parse_errors": sum(1 for r in results if r.get("parse_error")),
    }

    return evaluation


# ── Output formatting ─────────────────────────────────────────

def print_summary_table(evaluation: dict) -> None:
    """Print a formatted ASCII summary table."""
    print(f"\n{'=' * 60}")
    print(f"  {evaluation['persona_name']} ({evaluation['model']})")
    print(f"{'=' * 60}")
    print(f"  Prompts evaluated: {evaluation['total_prompts']}")
    print(f"  Consistency pairs: {evaluation['total_consistency_pairs']}")

    rt = evaluation["response_time_summary"]
    print(f"  Avg response time: {rt['mean']} ms")

    if evaluation["parse_errors"]:
        print(f"  Parse errors: {evaluation['parse_errors']}")

    print(f"\n  {'Dimension':<25} {'Mean':>5} {'Min':>5} {'Max':>5} {'StDev':>6}")
    print(f"  {'-' * 47}")

    for dim in ALL_DIMENSIONS:
        s = evaluation["summary"].get(dim.name, {})
        if s.get("count", 0) > 0:
            print(f"  {dim.display_name:<25} {s['mean']:>5.1f} "
                  f"{s['min']:>5} {s['max']:>5} {s['stdev']:>6.1f}")
        else:
            print(f"  {dim.display_name:<25}   n/a")

    cs = evaluation.get("consistency_summary", {})
    if cs.get("count", 0) > 0:
        print(f"\n  {'Consistency':<25} {cs['mean']:>5.1f} "
              f"{cs['min']:>5} {cs['max']:>5} {cs['stdev']:>6.1f}")

    print()


def save_results(evaluation: dict, output_dir: str = RESULTS_DIR) -> str:
    """Save evaluation results to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{evaluation['persona_id']}_{timestamp}.json"
    path = os.path.join(output_dir, filename)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2, default=str)

    return path


# ── CLI entry point ───────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate persona realism using LLM-as-judge scoring"
    )
    parser.add_argument(
        "--persona",
        default=None,
        help="Persona ID (e.g., tutor). Evaluates all if omitted.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model for persona")
    parser.add_argument("--judge-model", default=JUDGE_MODEL, help="Ollama model for judge")
    parser.add_argument("--category", default=None, help="Filter prompts by category")
    parser.add_argument("--output-dir", default=RESULTS_DIR, help="Directory for result files")
    parser.add_argument("--verbose", action="store_true", help="Show progress for each prompt")
    args = parser.parse_args()

    personas = load_all_personas()
    if not personas:
        print(f"Error: No persona files found in {PERSONAS_DIR}/")
        sys.exit(1)

    persona_ids = [args.persona] if args.persona else list(personas.keys())

    for pid in persona_ids:
        evaluation = run_evaluation(
            persona_id=pid,
            model=args.model,
            judge_model=args.judge_model,
            category=args.category,
            verbose=args.verbose,
        )
        print_summary_table(evaluation)

        path = save_results(evaluation, args.output_dir)
        print(f"  Results saved: {path}")

    if len(persona_ids) > 1:
        print(f"\nAll {len(persona_ids)} personas evaluated. "
              f"Results in {args.output_dir}/")


if __name__ == "__main__":
    main()
