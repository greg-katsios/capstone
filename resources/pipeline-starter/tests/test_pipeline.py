"""
tests for validation and full pipeline smoke test

run with: pytest tests/test_pipeline.py -v
"""

import pandas as pd
import pytest
from src.validate import validate, ArticleChunkSchema


# valid data should pass

def test_valid_data_passes_schema():
    df = pd.DataFrame({
        "id":           [1, 1],
        "title":        ["Test Article", "Test Article"],
        "body":         ["Full body text here"] * 2,
        "category":     ["tech", "tech"],
        "chunk_text":   ["This is a valid chunk with enough characters."] * 2,
        "chunk_index":  [0, 1],
        "chunk_id":     ["abc123", "def456"],
        "char_count":   [46, 46],
    })
    result = validate(df)
    assert len(result) == 2


# invalid category should fail

def test_invalid_category_fails():
    df = pd.DataFrame({
        "id":           [1],
        "title":        ["Test"],
        "body":         ["Body text"],
        "category":     ["INVALID_CATEGORY"],
        "chunk_text":   ["This is a valid chunk with enough characters."],
        "chunk_index":  [0],
        "chunk_id":     ["abc123"],
        "char_count":   [46],
    })
    with pytest.raises(Exception):  # Pandera raises SchemaError
        validate(df)


# smoke test: run the whole pipeline end to end

def test_full_pipeline_smoke():
    """runs the whole pipeline on sample data, just makes sure it doesn't crash."""
    from src.utils import load_config
    from src.ingest import ingest
    from src.clean import clean
    from src.chunk import chunk
    import tempfile, os

    config = load_config("config/config.yaml")

    # run all stages
    df = ingest(config["input_file"])
    df = clean(df, config["required_columns"], config.get("min_body_length", 50), config.get("dedup_columns"))
    df = chunk(df, separator=config.get("chunk_separator", "\n\n"), min_chunk_length=config.get("min_chunk_length", 20))
    df = validate(df)

    # basic sanity checks
    assert len(df) > 0, "Pipeline produced empty output"
    assert "chunk_text" in df.columns, "Missing chunk_text column"
    assert "chunk_id" in df.columns, "Missing chunk_id column"
    assert df["chunk_text"].isna().sum() == 0, "Found null chunks"

    # test export to temp file
    with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
        temp_path = f.name
    try:
        df.to_parquet(temp_path, index=False)
        reloaded = pd.read_parquet(temp_path)
        assert len(reloaded) == len(df), "Parquet round-trip row count mismatch"
    finally:
        os.unlink(temp_path)
