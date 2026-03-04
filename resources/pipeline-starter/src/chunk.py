"""
splits text into chunks and attaches metadata labels
"""

import pandas as pd
import hashlib
import logging

logger = logging.getLogger(__name__)


def chunk(
    df: pd.DataFrame,
    text_column: str = "body",
    separator: str = "\n\n",
    min_chunk_length: int = 20,
) -> pd.DataFrame:
    """splits text into chunks, keeps parent metadata.
    drops chunks shorter than min_chunk_length.
    returns a df with one row per chunk plus some extra columns."""
    rows_start = len(df)

    # split text into a list of chunks
    df = df.copy()
    df["_chunks"] = df[text_column].str.split(separator)

    # explode so each chunk gets its own row
    df = df.explode("_chunks").rename(columns={"_chunks": "chunk_text"})

    # strip whitespace from chunks
    df["chunk_text"] = df["chunk_text"].str.strip()

    # toss out empty or short chunks
    df = df[df["chunk_text"].str.len() >= min_chunk_length]

    # add chunk metadata
    df = df.reset_index(drop=True)
    df["chunk_index"] = df.groupby("id").cumcount()
    df["chunk_id"] = df.apply(
        lambda row: _make_chunk_id(row["id"], row["chunk_index"]), axis=1
    )
    df["char_count"] = df["chunk_text"].str.len()

    logger.info(
        f"chunking done: {rows_start} articles -> {len(df)} chunks "
        f"(avg {df['char_count'].mean():.0f} chars)"
    )
    return df


def _make_chunk_id(article_id, chunk_index: int) -> str:
    """makes a unique chunk id by hashing article id + chunk index."""
    raw = f"{article_id}-{chunk_index}"
    return hashlib.md5(raw.encode()).hexdigest()[:12]
