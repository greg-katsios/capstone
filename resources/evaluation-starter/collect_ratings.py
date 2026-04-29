"""
CLI tool for collecting human ratings on persona responses.

Presents each persona response one at a time and asks the rater
to score it on the rubric dimensions (1-5).  Saves ratings to
a JSON file for inter-rater reliability analysis.

Usage:
    python collect_ratings.py results/tutor_20260429_120000.json --rater-id alice
"""

import argparse
import json
import os
from datetime import datetime

from rubrics import ALL_DIMENSIONS, format_rubric_for_display


# ── Load evaluation results ───────────────────────────────────

def load_responses(results_file: str) -> list[dict]:
    """Load prompt-response pairs from an evaluation results file."""
    with open(results_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("results", [])


# ── Interactive rating collection ─────────────────────────────

def get_rating(dimension_name: str) -> int:
    """Prompt for a single 1-5 rating with input validation."""
    while True:
        raw = input(f"    {dimension_name} (1-5): ").strip()
        try:
            val = int(raw)
            if 1 <= val <= 5:
                return val
        except ValueError:
            pass
        print("    Please enter a number between 1 and 5.")


def collect_ratings_cli(responses: list[dict], rater_id: str) -> list[dict]:
    """Walk through each response and collect ratings interactively."""
    print(f"\n{'=' * 60}")
    print(f"  Human Rating Collection — Rater: {rater_id}")
    print(f"  {len(responses)} responses to rate")
    print(f"{'=' * 60}")
    print(f"\nRubric dimensions:\n")
    print(format_rubric_for_display())
    print(f"{'-' * 60}")

    ratings = []
    for i, resp in enumerate(responses):
        print(f"\n--- Response {i+1}/{len(responses)} [{resp.get('category', '?')}] ---")
        print(f"\nPrompt: {resp['prompt_text']}")
        print(f"\nResponse: {resp['response'][:500]}")
        if len(resp.get("response", "")) > 500:
            print(f"  ... ({len(resp['response'])} chars total)")

        print(f"\nRate this response:")
        scores = {}
        for dim in ALL_DIMENSIONS:
            scores[dim.name] = get_rating(dim.display_name)

        comment = input("    Comment (optional, press Enter to skip): ").strip()

        ratings.append({
            "prompt_id": resp.get("prompt_id", f"prompt_{i}"),
            "rater_id": rater_id,
            "scores": scores,
            "comment": comment if comment else None,
            "timestamp": datetime.now().isoformat(),
        })

        print(f"    Recorded: {scores}")

    return ratings


# ── Save ratings ──────────────────────────────────────────────

def save_ratings(
    ratings: list[dict],
    rater_id: str,
    persona_id: str,
    output_dir: str = "ratings",
) -> str:
    """Save collected ratings to a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{persona_id}_{rater_id}_{timestamp}.json"
    path = os.path.join(output_dir, filename)

    data = {
        "rater_id": rater_id,
        "persona_id": persona_id,
        "timestamp": datetime.now().isoformat(),
        "total_rated": len(ratings),
        "ratings": ratings,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return path


# ── CLI entry point ───────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Collect human ratings for persona responses"
    )
    parser.add_argument(
        "results_file",
        help="Path to evaluation results JSON (from evaluate.py)",
    )
    parser.add_argument(
        "--rater-id",
        required=True,
        help="Unique rater identifier (e.g., 'alice', 'rater_1')",
    )
    parser.add_argument(
        "--output-dir",
        default="ratings",
        help="Directory for rating files (default: ratings/)",
    )
    args = parser.parse_args()

    responses = load_responses(args.results_file)
    if not responses:
        print(f"No responses found in {args.results_file}")
        return

    # Extract persona ID from the results file
    with open(args.results_file, "r", encoding="utf-8") as f:
        meta = json.load(f)
    persona_id = meta.get("persona_id", "unknown")

    ratings = collect_ratings_cli(responses, args.rater_id)

    if ratings:
        path = save_ratings(ratings, args.rater_id, persona_id, args.output_dir)
        print(f"\n{'=' * 60}")
        print(f"  Ratings saved: {path}")
        print(f"  Total rated: {len(ratings)}")

        # Print rater summary
        for dim in ALL_DIMENSIONS:
            scores = [r["scores"][dim.name] for r in ratings]
            avg = sum(scores) / len(scores)
            print(f"  {dim.display_name}: avg {avg:.1f}")
        print()


if __name__ == "__main__":
    main()
