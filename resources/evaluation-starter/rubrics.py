"""
Qualitative rubric definitions for persona evaluation.

Defines four rating dimensions with 1-5 anchor descriptions.
Used by evaluate.py (LLM-as-judge prompts) and collect_ratings.py
(human rating interface).

Usage:
    from rubrics import ALL_DIMENSIONS, format_rubric_for_llm
    print(format_rubric_for_llm())
"""

from dataclasses import dataclass, field


# ── Rubric dimension ──────────────────────────────────────────

@dataclass
class RubricDimension:
    name: str
    display_name: str
    description: str
    anchors: dict[int, str] = field(default_factory=dict)
    scale_min: int = 1
    scale_max: int = 5


# ── Dimension definitions ─────────────────────────────────────

PSYCHOLOGICAL_DEPTH = RubricDimension(
    name="psychological_depth",
    display_name="Psychological Depth",
    description="Does the persona feel like it has a rich inner life?",
    anchors={
        1: "Flat, scripted feel. Responses could come from any generic chatbot.",
        2: "Occasionally hints at personality but mostly surface-level.",
        3: "Shows a consistent perspective and some personal opinions.",
        4: "Demonstrates nuanced thinking, preferences, and self-awareness.",
        5: "Rich inner life, nuanced reactions. Feels like a real person with experiences and opinions.",
    },
)

EMOTIONAL_REALISM = RubricDimension(
    name="emotional_realism",
    display_name="Emotional Realism",
    description="Does the persona respond with appropriate, varied emotions?",
    anchors={
        1: "No emotional range. Flat tone regardless of context.",
        2: "Acknowledges emotions but responses feel formulaic.",
        3: "Shows some emotional variation but responses sometimes feel templated.",
        4: "Emotional responses are usually appropriate and feel natural.",
        5: "Appropriate, varied emotional responses that match the context and persona role.",
    },
)

NARRATIVE_COHERENCE = RubricDimension(
    name="narrative_coherence",
    display_name="Narrative Coherence",
    description="Does the persona maintain a consistent identity and backstory?",
    anchors={
        1: "Contradicts itself across responses. No consistent identity.",
        2: "Loosely consistent but sometimes breaks character.",
        3: "Mostly consistent identity with occasional lapses.",
        4: "Strong consistency. Rarely breaks character or contradicts prior statements.",
        5: "Maintains consistent backstory, perspective, and memory throughout.",
    },
)

HUMAN_LIKENESS = RubricDimension(
    name="human_likeness",
    display_name="Human Likeness",
    description="Could this response pass for one written by a real person?",
    anchors={
        1: "Obviously AI. Generic phrasing, excessive hedging, disclaimer language.",
        2: "Mostly AI-sounding with occasional natural moments.",
        3: "Could be either AI or human. Some natural phrasing mixed with generic patterns.",
        4: "Reads naturally. Only subtle cues suggest AI origin.",
        5: "Could pass for a real person in a blind test. Natural voice, specific details.",
    },
)


# ── Registry ──────────────────────────────────────────────────

ALL_DIMENSIONS: list[RubricDimension] = [
    PSYCHOLOGICAL_DEPTH,
    EMOTIONAL_REALISM,
    NARRATIVE_COHERENCE,
    HUMAN_LIKENESS,
]


def get_dimension_by_name(name: str) -> RubricDimension | None:
    for dim in ALL_DIMENSIONS:
        if dim.name == name:
            return dim
    return None


# ── Formatting helpers ────────────────────────────────────────

def format_rubric_for_llm(dimensions: list[RubricDimension] | None = None) -> str:
    """Format rubric dimensions as a structured prompt for an LLM judge."""
    dims = dimensions or ALL_DIMENSIONS
    lines = ["Rate the response on these dimensions (1-5 each):", ""]
    for dim in dims:
        lines.append(f"### {dim.display_name}")
        lines.append(dim.description)
        for score, anchor in sorted(dim.anchors.items()):
            lines.append(f"  {score} = {anchor}")
        lines.append("")
    return "\n".join(lines)


def format_rubric_for_display(dimensions: list[RubricDimension] | None = None) -> str:
    """Format rubric dimensions for human-readable display."""
    dims = dimensions or ALL_DIMENSIONS
    lines = []
    for dim in dims:
        lines.append(f"  {dim.display_name}: {dim.description}")
        for score, anchor in sorted(dim.anchors.items()):
            lines.append(f"    [{score}] {anchor}")
        lines.append("")
    return "\n".join(lines)
