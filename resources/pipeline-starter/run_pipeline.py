#!/usr/bin/env python3
"""
main entry point for the data prep pipeline

usage:
    python run_pipeline.py                          # run all stages
    python run_pipeline.py --config config/my.yaml  # custom config
    python run_pipeline.py --stage clean             # run one stage only

stages: ingest, clean, chunk, validate, export, all
"""

import argparse
import logging
import sys

from src.utils import setup_logging, load_config
from src.ingest import ingest
from src.clean import clean
from src.chunk import chunk
from src.validate import validate
from src.export import export

logger = logging.getLogger("pipeline")


def run_pipeline(config: dict, stage: str = "all") -> None:
    """runs pipeline stages based on config and the stage you picked."""

    # stage 1: ingest
    if stage in ("all", "ingest"):
        logger.info("stage 1: ingest")
        df = ingest(
            filepath=config["input_file"],
            encoding=config.get("encoding", "utf-8"),
        )
        if stage == "ingest":
            print(df.head())
            return

    # stage 2: clean
    if stage in ("all", "clean"):
        logger.info("stage 2: clean")
        if stage == "clean":
            df = ingest(config["input_file"], config.get("encoding", "utf-8"))
        df = clean(
            df,
            required_columns=config["required_columns"],
            min_body_length=config.get("min_body_length", 50),
            dedup_columns=config.get("dedup_columns"),
        )
        if stage == "clean":
            print(df.head())
            return

    # stage 3: chunk
    if stage in ("all", "chunk"):
        logger.info("stage 3: chunk")
        if stage == "chunk":
            df = ingest(config["input_file"], config.get("encoding", "utf-8"))
            df = clean(df, config["required_columns"], config.get("min_body_length", 50), config.get("dedup_columns"))
        df = chunk(
            df,
            text_column=config.get("text_column", "body"),
            separator=config.get("chunk_separator", "\n\n"),
            min_chunk_length=config.get("min_chunk_length", 20),
        )
        if stage == "chunk":
            print(df[["id", "title", "chunk_index", "char_count", "chunk_text"]].head(10))
            return

    # stage 4: validate and export
    if stage in ("all", "validate", "export"):
        logger.info("stage 4: validate and export")
        if stage in ("validate", "export"):
            df = ingest(config["input_file"], config.get("encoding", "utf-8"))
            df = clean(df, config["required_columns"], config.get("min_body_length", 50), config.get("dedup_columns"))
            df = chunk(df, text_column=config.get("text_column", "body"), separator=config.get("chunk_separator", "\n\n"), min_chunk_length=config.get("min_chunk_length", 20))
        df = validate(df)
        export(
            df,
            output_path=config["output_file"],
            data_card_path=config["data_card_file"],
        )

    # done
    logger.info("pipeline complete")
    logger.info(f"output: {config['output_file']}")
    logger.info(f"data card: {config['data_card_file']}")


def main():
    parser = argparse.ArgumentParser(description="Data Preparation Pipeline")
    parser.add_argument(
        "--config", default="config/config.yaml",
        help="Path to config file (default: config/config.yaml)"
    )
    parser.add_argument(
        "--stage", default="all",
        choices=["all", "ingest", "clean", "chunk", "validate", "export"],
        help="Which stage to run (default: all)"
    )
    args = parser.parse_args()

    setup_logging()
    config = load_config(args.config)
    logger.info(f"loaded config from {args.config}")

    try:
        run_pipeline(config, stage=args.stage)
    except Exception as e:
        logger.error(f"pipeline failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
