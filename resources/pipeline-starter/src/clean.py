"""
cleans up the data, handles nulls, removes duplicates
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


def clean(
    df: pd.DataFrame,
    required_columns: list[str],
    min_body_length: int = 50,
    dedup_columns: list[str] | None = None,
) -> pd.DataFrame:
    """removes bad rows and duplicates from the dataframe.
    returns a cleaned up version."""
    rows_start = len(df)

    # drop rows missing required columns
    df = df.dropna(subset=required_columns)
    logger.info(f"dropped nulls in {required_columns}: {len(df)} rows (was {rows_start})")

    # filter out short bodies
    if "body" in df.columns:
        df = df[df["body"].str.len() >= min_body_length]
        logger.info(f"after min body length ({min_body_length}): {len(df)} rows")

    # strip whitespace from title
    if "title" in df.columns:
        df["title"] = df["title"].str.strip()

    # lowercase the category
    if "category" in df.columns:
        df["category"] = df["category"].str.lower().str.strip()

    # remove duplicates
    if dedup_columns:
        rows_before_dedup = len(df)
        df = df.drop_duplicates(subset=dedup_columns, keep="first")
        dupes_removed = rows_before_dedup - len(df)
        logger.info(f"removed {dupes_removed} duplicates on {dedup_columns}: {len(df)} rows left")

    # reset index
    df = df.reset_index(drop=True)

    logger.info(f"cleaning done: {rows_start} -> {len(df)} rows")
    return df
