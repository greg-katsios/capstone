"""
tests for the cleaning module

run with: pytest tests/test_clean.py -v
"""

import pandas as pd
from src.clean import clean


def _make_df(rows: list[dict]) -> pd.DataFrame:
    """quick helper to make a small df from a list of dicts."""
    return pd.DataFrame(rows)


# null handling

def test_drops_rows_with_null_title():
    df = _make_df([
        {"title": "Hello World",  "body": "x" * 100, "category": "tech"},
        {"title": None,           "body": "y" * 100, "category": "tech"},
        {"title": "Another Post", "body": "z" * 100, "category": "science"},
    ])
    result = clean(df, required_columns=["title", "body"])
    assert len(result) == 2
    assert result["title"].isna().sum() == 0


def test_drops_rows_with_null_body():
    df = _make_df([
        {"title": "Has body",    "body": "x" * 100, "category": "tech"},
        {"title": "Missing body", "body": None,      "category": "tech"},
    ])
    result = clean(df, required_columns=["title", "body"])
    assert len(result) == 1


# minimum body length

def test_filters_short_bodies():
    df = _make_df([
        {"title": "Long enough",  "body": "x" * 100, "category": "tech"},
        {"title": "Too short",    "body": "hi",       "category": "tech"},
    ])
    result = clean(df, required_columns=["title", "body"], min_body_length=50)
    assert len(result) == 1
    assert result.iloc[0]["title"] == "Long enough"


# whitespace stripping

def test_strips_title_whitespace():
    df = _make_df([
        {"title": "  hello world  ", "body": "x" * 100, "category": "tech"},
    ])
    result = clean(df, required_columns=["title", "body"])
    assert result.iloc[0]["title"] == "hello world"


# deduplication

def test_removes_exact_duplicates():
    df = _make_df([
        {"title": "Same Title", "body": "Same body " * 20, "category": "tech"},
        {"title": "Same Title", "body": "Same body " * 20, "category": "tech"},
        {"title": "Different",  "body": "Other body " * 20, "category": "science"},
    ])
    result = clean(df, required_columns=["title"], dedup_columns=["title", "body"])
    assert len(result) == 2


# category normalization

def test_normalizes_category_case():
    df = _make_df([
        {"title": "Post", "body": "x" * 100, "category": "  TECH  "},
    ])
    result = clean(df, required_columns=["title", "body"])
    assert result.iloc[0]["category"] == "tech"
