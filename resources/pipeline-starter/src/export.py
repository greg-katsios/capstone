"""
saves the prepared dataset to parquet and makes a data card
"""

import pandas as pd
import hashlib
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


def export(df: pd.DataFrame, output_path: str, data_card_path: str) -> None:
    """saves the df to parquet and writes a data card yaml."""
    # make sure the output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # save to parquet
    df.to_parquet(output_path, index=False)
    logger.info(f"exported {len(df)} rows to {output_path}")

    # generate data card
    data_hash = hashlib.md5(pd.util.hash_pandas_object(df).values.tobytes()).hexdigest()[:16]
    timestamp = datetime.now().isoformat(timespec="seconds")

    card = _build_data_card(df, output_path, data_hash, timestamp)

    with open(data_card_path, "w") as f:
        f.write(card)
    logger.info(f"data card written to {data_card_path}")


def _build_data_card(
    df: pd.DataFrame, output_path: str, data_hash: str, timestamp: str
) -> str:
    """builds a plain text data card that describes the dataset."""
    lines = [
        "# Data Card",
        f"# Generated: {timestamp}",
        "",
        "dataset:",
        f"  file: {output_path}",
        f"  hash: {data_hash}",
        f"  rows: {len(df)}",
        f"  columns: {len(df.columns)}",
        "",
        "schema:",
    ]

    for col in df.columns:
        dtype = str(df[col].dtype)
        null_pct = df[col].isna().mean() * 100
        lines.append(f"  {col}:")
        lines.append(f"    dtype: {dtype}")
        lines.append(f"    null_pct: {null_pct:.1f}%")

        # throw in value counts for categorical columns
        if df[col].dtype == "object" and df[col].nunique() <= 10:
            lines.append(f"    unique_values: {sorted(df[col].dropna().unique().tolist())}")

    lines += [
        "",
        "stats:",
        f"  total_chunks: {len(df)}",
    ]

    if "char_count" in df.columns:
        lines += [
            f"  avg_chunk_length: {df['char_count'].mean():.0f}",
            f"  min_chunk_length: {df['char_count'].min()}",
            f"  max_chunk_length: {df['char_count'].max()}",
        ]

    if "category" in df.columns:
        lines.append("  category_distribution:")
        for cat, count in df["category"].value_counts().items():
            lines.append(f"    {cat}: {count}")

    lines += [
        "",
        "lineage:",
        f"  pipeline_version: v1",
        f"  processed_at: {timestamp}",
    ]

    return "\n".join(lines) + "\n"
