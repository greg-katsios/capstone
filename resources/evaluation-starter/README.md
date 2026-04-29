# Evaluation Starter Kit

This starter helps you figure out how realistic your personas actually are. It sends test prompts to your personas through Ollama, then uses a second LLM call (the "judge") to score each response on a 1-5 scale across four dimensions. You can also collect ratings from real humans and see how well they agree with each other.

No numpy, scipy, or pandas needed. Everything runs on plain Python.


## Quick Start

You need Python 3.10+, Ollama running, and a model pulled:

    ollama pull llama3.1

Then install and run:

    cd resources/evaluation-starter
    pip install -r requirements.txt
    python evaluate.py --persona tutor --verbose

You'll see it work through each prompt, then print a summary table with scores. To evaluate all three personas at once:

    python evaluate.py --verbose


## What's in here

evaluate.py -- The main script. Sends prompts to your persona, collects responses, then has the LLM judge score them. Saves results to a JSON file in results/.

rubrics.py -- Defines the four things we score on: psychological depth, emotional realism, narrative coherence, and human likeness. Each has a 1-5 scale with descriptions at every level so raters know what a "3" actually means.

metrics.py -- Math stuff. Pearson correlation, Cohen's Kappa, mean absolute error, and Krippendorff's alpha. All written in pure Python so you can read the code and see how they work.

collect_ratings.py -- A command-line tool for human raters. Shows each persona response and asks for 1-5 scores on each dimension. Saves everything to a JSON file in ratings/.

test_prompts.json -- 25 test prompts split across five categories: factual (6), emotional (5), personal (4), consistency (5), and edge cases (5).

personas/ -- The same persona YAML files from the telemetry starter (tutor, coach, analyst).

requirements.txt -- Just ollama and pyyaml. That's it.

EXERCISES.md -- Your assignment. Five exercises, three required, two stretch.

The script also creates these at runtime:
- results/ -- JSON files with all the scores, response times, and judge explanations
- ratings/ -- JSON files from human raters (when you use collect_ratings.py)


## How it works

For each test prompt, the script does two things:

1. Sends the prompt to your persona through Ollama and records the response plus how long it took.

2. Sends that response (along with the persona definition and the rubric) to a second LLM call. This "judge" scores the response 1-5 on each dimension and writes a brief justification.

For consistency prompts (same question asked two different ways), it sends both versions separately, then asks the judge how consistent the two answers are.

At the end you get a summary table and a JSON file with everything.

The four scoring dimensions are:
- Psychological depth -- does the persona feel like it has a real inner life?
- Emotional realism -- does it respond with appropriate emotions?
- Narrative coherence -- does it stay in character and not contradict itself?
- Human likeness -- could this pass for something a real person wrote?


## Command line options

evaluate.py:

    python evaluate.py [options]

    --persona PERSONA    Which persona to evaluate (e.g. tutor). Does all if you skip this.
    --model MODEL        Ollama model for the persona (default: llama3.1)
    --judge-model MODEL  Ollama model for the judge (default: llama3.1)
    --category CATEGORY  Only run prompts from one category (e.g. emotional)
    --output-dir DIR     Where to save results (default: results/)
    --verbose            Print progress as it goes

collect_ratings.py:

    python collect_ratings.py RESULTS_FILE --rater-id ID

    RESULTS_FILE         Path to a results JSON from evaluate.py
    --rater-id ID        A name for the rater (e.g. alice, rater_1). Required.
    --output-dir DIR     Where to save ratings (default: ratings/)


## Which models work

Any Ollama model works here since evaluation uses plain chat, not tool calling. llama3.1 is recommended but mistral, qwen2.5, and llama3.2 all work fine.


## Troubleshooting

"No module named ollama" -- Run pip install -r requirements.txt

Connection error -- Make sure Ollama is running with ollama serve

Model not found -- Run ollama pull llama3.1 (or whatever model you want)

Judge returns weird output -- Some models don't always return clean JSON. The parser has fallbacks built in. Check the parse_errors count in your results file.

It's slow -- That's expected. Each persona takes about 2-5 minutes because it makes 2 LLM calls per prompt (one for the response, one for the judge). 25 prompts = 50 calls.

Import errors for rubrics or metrics -- Make sure you're running from inside the evaluation-starter/ directory.

No persona files found -- Same thing, run from evaluation-starter/.


## Next steps

Check out EXERCISES.md for the full assignment. You'll run the evaluator, write your own test prompts, collect human ratings, and calculate whether your raters actually agree with each other.
