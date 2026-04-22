"""
Tool definitions for the Research-Grade Persona Chat.

Each tool is a plain Python function with type hints and a docstring.
Ollama auto-generates the JSON schema from these, so the function
signature IS the tool schema.

These tools use st.session_state for storage, so they must be called
within a running Streamlit app context.
"""

import json
from datetime import datetime
from typing import Optional

import streamlit as st


# ── Memory helpers ──────────────────────────────────────────────

def _get_memory() -> dict:
    """Return the shared memory dict from session state."""
    if "memory" not in st.session_state:
        st.session_state.memory = {}
    return st.session_state.memory


# ── Tool functions ──────────────────────────────────────────────

def save_memory(key: str, value: str) -> str:
    """Save a piece of information to memory for later recall.

    Args:
        key: A short label for this memory (e.g. 'user_name', 'favorite_color').
        value: The information to remember.

    Returns:
        Confirmation message.
    """
    memory = _get_memory()
    memory[str(key)] = str(value)
    return f"Saved to memory: {key} = {value}"


def recall_memory(key: Optional[str] = None) -> str:
    """Recall previously saved information from memory.

    Args:
        key: Optional specific memory key to retrieve. If not provided, returns all memories.

    Returns:
        The recalled memory or all memories.
    """
    memory = _get_memory()
    key = str(key).strip() if key else ""
    if key and key in memory:
        return f"{key}: {memory[key]}"
    elif key:
        return f"No memory found for key: {key}"
    else:
        if not memory:
            return "No memories saved yet."
        return json.dumps(memory, indent=2)


def get_current_context() -> str:
    """Get current date/time and conversation context information.

    Returns:
        JSON string with current timestamp and conversation stats.
    """
    msg_count = len(st.session_state.get("messages", []))
    now = datetime.now()
    return json.dumps({
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "messages_in_conversation": msg_count,
    }, indent=2)


def submit_feedback(rating: str, comment: str = "") -> str:
    """Submit feedback about the current conversation.

    Args:
        rating: Either 'positive' or 'negative'.
        comment: Optional free-text comment explaining the rating.

    Returns:
        Confirmation message.
    """
    feedback = {
        "rating": rating,
        "comment": comment,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    if "feedback_log" not in st.session_state:
        st.session_state.feedback_log = []
    st.session_state.feedback_log.append(feedback)
    return f"Feedback recorded: {rating}" + (f" — {comment}" if comment else "")


# ── Registry ────────────────────────────────────────────────────

TOOL_FUNCTIONS: dict = {
    "save_memory": save_memory,
    "recall_memory": recall_memory,
    "get_current_context": get_current_context,
    "submit_feedback": submit_feedback,
}

ALL_TOOLS: list = [save_memory, recall_memory, get_current_context, submit_feedback]


def get_tools_for_persona(persona: dict) -> list:
    """Return the tool list for a given persona.

    If the persona YAML has a 'tools' field, filter to those tools only.
    Otherwise return all tools.
    """
    allowed = persona.get("tools")
    if allowed:
        return [fn for name, fn in TOOL_FUNCTIONS.items() if name in allowed]
    return list(ALL_TOOLS)
