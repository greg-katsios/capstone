"""
loads raw data and standardizes column names, types, and formats
"""

import pandas as pd
import logging

logger = logging.getLogger(__name__)


def ingest(filepath: str, encoding: str = "utf-8") -> pd.DataFrame:
    """loads a csv and normalizes column names and types."""
    # load the csv
    df = pd.read_csv(filepath, encoding=encoding)
    logger.info(f"loaded {len(df)} rows from {filepath}")

    # clean up column names (lowercase, no spaces)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    logger.info(f"columns: {list(df.columns)}")

    # strip whitespace from string columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # parse dates
    if "publish_date" in df.columns:
        df["publish_date"] = pd.to_datetime(df["publish_date"], errors="coerce")

    # make sure id is an integer
    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")

    logger.info(f"normalized: {len(df)} rows, dtypes:\n{df.dtypes}")
    return df
