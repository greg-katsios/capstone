import math
from copy import deepcopy
from pathlib import Path

import pandas as pd
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

# --------------------
# Config
# --------------------
BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
BASE_DIR = Path(__file__).resolve().parent
ADAPTER_DIR = BASE_DIR / "tinyllama_1p1b_hippo_recalled_lora_mps"
VAL_CSV = BASE_DIR / "val_stories.csv"
OUT_DIR = BASE_DIR / "phase3_outputs"

SEED = 42
MAX_LEN = 256
PPL_BATCH_SIZE = 2
MAX_NEW_TOKENS = 150

PROMPTS = [
    "I remember the day when",
    "That summer my family",
    "The hardest thing I ever",
    "One moment I will never forget",
    "Last year, I realized",
]

FIRST_PERSON_PRONOUNS = {
    "i",
    "me",
    "my",
    "mine",
    "myself",
    "we",
    "us",
    "our",
    "ours",
    "ourselves",
}


def clean_text(value: str) -> str:
    return " ".join(str(value).split()).strip()


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_validation_stories(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Validation file not found: {path}")

    df = pd.read_csv(path)
    if "story" not in df.columns:
        raise ValueError(f"Expected a 'story' column in {path}")

    stories = [clean_text(s) for s in df["story"].astype(str).tolist()]
    stories = [s for s in stories if s]
    if not stories:
        raise ValueError("No non-empty validation stories were found.")
    return stories


def load_models_and_tokenizer(device: torch.device):
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    dtype = torch.float16 if device.type in {"cuda", "mps"} else torch.float32

    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )
    base_model.to(device)
    base_model.eval()

    if not ADAPTER_DIR.exists():
        raise FileNotFoundError(f"Adapter directory not found: {ADAPTER_DIR}")

    adapted_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=dtype,
        low_cpu_mem_usage=True,
    )
    adapted_model = PeftModel.from_pretrained(adapted_model, str(ADAPTER_DIR))
    adapted_model.to(device)
    adapted_model.eval()

    return tokenizer, base_model, adapted_model


def compute_perplexity(model, tokenizer, texts: list[str], device: torch.device) -> float:
    total_nll = 0.0
    total_tokens = 0

    for i in range(0, len(texts), PPL_BATCH_SIZE):
        batch = texts[i : i + PPL_BATCH_SIZE]
        enc = tokenizer(
            batch,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_LEN,
            padding=True,
        )
        enc = {k: v.to(device) for k, v in enc.items()}

        labels = enc["input_ids"].clone()
        labels[enc["attention_mask"] == 0] = -100

        with torch.no_grad():
            outputs = model(**enc, labels=labels)

        token_count = int((labels != -100).sum().item())
        total_nll += float(outputs.loss.item()) * token_count
        total_tokens += token_count

    if total_tokens == 0:
        raise ValueError("Perplexity computation had zero target tokens.")

    avg_nll = total_nll / total_tokens
    return float(math.exp(avg_nll))


def generate_outputs(model, tokenizer, prompts: list[str], device: torch.device) -> list[dict]:
    rows = []
    # Avoid generation warnings when model config has max_length set and we use max_new_tokens.
    generation_config = deepcopy(model.generation_config)
    generation_config.max_length = None

    for prompt in prompts:
        inputs = tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                generation_config=generation_config,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )

        full_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        continuation = full_text[len(prompt) :].strip() if full_text.startswith(prompt) else full_text

        rows.append(
            {
                "prompt": prompt,
                "generated_text": full_text,
                "continuation_only": continuation,
            }
        )

    return rows


def _get_nltk_helpers():
    try:
        import nltk
        from nltk import pos_tag, word_tokenize
    except ImportError as exc:
        raise ImportError(
            "nltk is required for lexical analysis. Install with: pip install nltk"
        ) from exc

    # Download resources only if missing.
    for resource, path in [
        ("punkt", "tokenizers/punkt"),
        ("averaged_perceptron_tagger", "taggers/averaged_perceptron_tagger"),
        ("averaged_perceptron_tagger_eng", "taggers/averaged_perceptron_tagger_eng"),
    ]:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource, quiet=True)

    return word_tokenize, pos_tag


def compute_lexical_metrics(texts: list[str]) -> dict:
    word_tokenize, pos_tag = _get_nltk_helpers()

    all_tokens = []
    alpha_tokens = []
    first_person_count = 0
    past_tense_count = 0

    for text in texts:
        tokens = word_tokenize(text)
        tokens_lower = [t.lower() for t in tokens]
        all_tokens.extend(tokens_lower)

        alpha_only = [t for t in tokens_lower if t.isalpha()]
        alpha_tokens.extend(alpha_only)

        first_person_count += sum(1 for t in tokens_lower if t in FIRST_PERSON_PRONOUNS)

        tagged = pos_tag(tokens)
        past_tense_count += sum(1 for _, tag in tagged if tag in {"VBD", "VBN"})

    total_tokens = len(all_tokens) or 1
    total_alpha_tokens = len(alpha_tokens) or 1
    unique_alpha_tokens = len(set(alpha_tokens))

    return {
        "first_person_count": first_person_count,
        "first_person_rate": first_person_count / total_tokens,
        "past_tense_count": past_tense_count,
        "past_tense_rate": past_tense_count / total_tokens,
        "type_token_ratio": unique_alpha_tokens / total_alpha_tokens,
        "total_tokens": total_tokens,
    }


def write_outputs(
    base_ppl: float,
    adapted_ppl: float,
    base_generations: list[dict],
    adapted_generations: list[dict],
    base_lex: dict,
    adapted_lex: dict,
):
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ppl_delta_abs = base_ppl - adapted_ppl
    ppl_delta_pct = (ppl_delta_abs / base_ppl * 100.0) if base_ppl != 0 else 0.0

    ppl_df = pd.DataFrame(
        [
            {
                "model": "base",
                "perplexity": base_ppl,
            },
            {
                "model": "adapted",
                "perplexity": adapted_ppl,
            },
            {
                "model": "delta",
                "perplexity": ppl_delta_abs,
            },
        ]
    )
    ppl_df.to_csv(OUT_DIR / "metric1_perplexity.csv", index=False)

    gen_rows = []
    for b, a in zip(base_generations, adapted_generations):
        gen_rows.append(
            {
                "prompt": b["prompt"],
                "base_generated": b["generated_text"],
                "adapted_generated": a["generated_text"],
                "base_emotional_specificity_1_to_5": "",
                "base_temporal_grounding_1_to_5": "",
                "base_first_person_consistency_1_to_5": "",
                "adapted_emotional_specificity_1_to_5": "",
                "adapted_temporal_grounding_1_to_5": "",
                "adapted_first_person_consistency_1_to_5": "",
                "notes": "",
            }
        )

    pd.DataFrame(gen_rows).to_csv(OUT_DIR / "metric2_generation_rubric.csv", index=False)

    lex_df = pd.DataFrame(
        [
            {
                "model": "base",
                **base_lex,
            },
            {
                "model": "adapted",
                **adapted_lex,
            },
            {
                "model": "delta_adapted_minus_base",
                "first_person_count": adapted_lex["first_person_count"] - base_lex["first_person_count"],
                "first_person_rate": adapted_lex["first_person_rate"] - base_lex["first_person_rate"],
                "past_tense_count": adapted_lex["past_tense_count"] - base_lex["past_tense_count"],
                "past_tense_rate": adapted_lex["past_tense_rate"] - base_lex["past_tense_rate"],
                "type_token_ratio": adapted_lex["type_token_ratio"] - base_lex["type_token_ratio"],
                "total_tokens": adapted_lex["total_tokens"] - base_lex["total_tokens"],
            },
        ]
    )
    lex_df.to_csv(OUT_DIR / "metric3_lexical.csv", index=False)

    summary_md = f"""# Phase 3 Evaluation Summary

## Metric 1: Perplexity
- Base perplexity: {base_ppl:.4f}
- Adapted perplexity: {adapted_ppl:.4f}
- Absolute drop (base - adapted): {ppl_delta_abs:.4f}
- Percent drop: {ppl_delta_pct:.2f}%

Interpretation note:
- Lower perplexity is better because it means lower average negative log-likelihood on held-out stories.
- Use percent drop to judge impact: small (<3%), meaningful (5-10%), strong (>10%).

## Metric 2: Narrative Generation Quality
- File: metric2_generation_rubric.csv
- Next step: manually score each output from 1-5 on emotional specificity, temporal grounding, and first-person consistency.

## Metric 3: Lexical Analysis
- File: metric3_lexical.csv
- Includes first-person pronoun frequency, past-tense verb frequency, and type-token ratio.
"""

    (OUT_DIR / "phase3_summary.md").write_text(summary_md, encoding="utf-8")


def main():
    torch.manual_seed(SEED)

    print("Loading validation stories...")
    stories = load_validation_stories(VAL_CSV)
    print(f"Validation examples: {len(stories)}")

    device = get_device()
    print("Using device:", device)

    tokenizer, base_model, adapted_model = load_models_and_tokenizer(device)

    print("Computing perplexity for base model...")
    base_ppl = compute_perplexity(base_model, tokenizer, stories, device)
    print(f"Base model complexity: {base_ppl:.4f}")

    print("Computing perplexity for adapted model...")
    adapted_ppl = compute_perplexity(adapted_model, tokenizer, stories, device)
    print(f"Adapated Model Complexity: {adapted_ppl:.4f}")

    print("Generating prompt outputs for both models...")
    base_generations = generate_outputs(base_model, tokenizer, PROMPTS, device)
    adapted_generations = generate_outputs(adapted_model, tokenizer, PROMPTS, device)

    print("\nBase Model Prompt Output")
    for row in base_generations:
        print(f"Prompt: {row['prompt']}")
        print(f"Output: {row['generated_text']}")
        print()

    print("Adapted Model Prompt Output")
    for row in adapted_generations:
        print(f"Prompt: {row['prompt']}")
        print(f"Output: {row['generated_text']}")
        print()

    print("Computing Lexical Metrics with NLTK")
    base_lex = compute_lexical_metrics([row["continuation_only"] for row in base_generations])
    adapted_lex = compute_lexical_metrics([row["continuation_only"] for row in adapted_generations])

    # print("Writing output files...")
    # write_outputs(
    #     base_ppl=base_ppl,
    #     adapted_ppl=adapted_ppl,
    #     base_generations=base_generations,
    #     adapted_generations=adapted_generations,
    #     base_lex=base_lex,
    #     adapted_lex=adapted_lex,
    # )

    print("Done. Outputs are in:", OUT_DIR)
    print("Done!")


if __name__ == "__main__":
    main()
