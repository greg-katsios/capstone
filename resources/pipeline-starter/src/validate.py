"""
validates the final dataframe against a schema before export
"""

import pandera.pandas as pa
import pandas as pd
import logging

logger = logging.getLogger(__name__)


# the expected schema for our output

class ArticleChunkSchema(pa.DataFrameModel):
    """schema for the final chunked articles dataset."""

    id:           int   = pa.Field(ge=1)
    title:        str   = pa.Field(str_length={"min_value": 1})
    category:     str   = pa.Field(isin=["tech", "science", "business", "health"])
    chunk_text:   str   = pa.Field(str_length={"min_value": 20})
    chunk_index:  int   = pa.Field(ge=0)
    chunk_id:     str   = pa.Field()
    char_count:   int   = pa.Field(ge=20)


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """checks the df against the schema. throws if something's wrong."""
    logger.info(f"validating {len(df)} rows against ArticleChunkSchema...")

    validated_df = ArticleChunkSchema.validate(df)

    logger.info("validation passed, all rows match the schema")
    return validated_df
