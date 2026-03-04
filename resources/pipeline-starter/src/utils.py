"""
logging setup and helper functions used across the pipeline
"""

import logging
import yaml


def setup_logging(level: str = "INFO") -> None:
    """sets up logging for the pipeline."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def load_config(config_path: str) -> dict:
    """loads a yaml config file and returns it as a dict."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config
