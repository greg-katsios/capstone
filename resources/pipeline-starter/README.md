# Data Preparation Pipeline

This is the starter code for the Data Preparation Sprint (Module 4). It takes a messy CSV of articles, cleans it up, splits the text into chunks, validates everything, and spits out a nice Parquet file at the end.


## How to run it

First, install the dependencies:

    pip install -r requirements.txt

Then run the pipeline:

    python run_pipeline.py

That's it. When it's done you'll find the output in data/processed/.

If you want to run the tests:

    pytest tests/ -v


## What the pipeline does

There are 4 stages and they run in order:

1. Ingest (src/ingest.py) - Loads the CSV, cleans up column names, fixes types and dates.
2. Clean (src/clean.py) - Drops rows with missing data, filters out short articles, removes duplicates.
3. Chunk (src/chunk.py) - Splits article bodies into smaller paragraph-sized pieces and tags each one with an ID and character count.
4. Validate and Export (src/validate.py + src/export.py) - Checks that the data matches the expected schema using Pandera, then saves it as a Parquet file along with a data card.


## Running a single stage

You don't have to run the whole thing every time. You can pick a stage:

    python run_pipeline.py --stage ingest
    python run_pipeline.py --stage clean
    python run_pipeline.py --stage chunk
    python run_pipeline.py --stage validate


## Configuration

All the settings are in config/config.yaml. If you need to change things like minimum body length, which columns to deduplicate on, or file paths, do it there. Don't hardcode stuff in the Python files.


## Project layout

- run_pipeline.py - the main entry point, ties everything together
- src/ - all the pipeline stage code lives here
- tests/ - unit tests and a smoke test for the full pipeline
- config/config.yaml - all the settings
- data/raw/articles.csv - the sample input data (intentionally messy)
- data/processed/ - where the output goes


## About the sample data

The file data/raw/articles.csv has 10 rows of intentionally bad data so you can see the pipeline handle real-world issues. There are duplicate articles, missing titles, missing bodies, extra whitespace all over the place, and a row with a body that's too short to be useful. The pipeline handles all of it.


## Output

After running, check data/processed/ for two files:

- articles_prepared.parquet - the clean, chunked dataset ready for downstream use
- data_card.yaml - a summary of the dataset with schema info, stats, and lineage
