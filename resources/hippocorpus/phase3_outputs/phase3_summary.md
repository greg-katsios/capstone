# Phase 3 Evaluation Summary

## Metric 1: Perplexity
- Base perplexity: 11.9058
- Adapted perplexity: 10.2338
- Absolute drop (base - adapted): 1.6720
- Percent drop: 14.04%

Interpretation note:
- Lower perplexity is better because it means lower average negative log-likelihood on held-out stories.
- Use percent drop to judge impact: small (<3%), meaningful (5-10%), strong (>10%).

## Metric 2: Narrative Generation Quality
- File: metric2_generation_rubric.csv
- Next step: manually score each output from 1-5 on emotional specificity, temporal grounding, and first-person consistency.

## Metric 3: Lexical Analysis
- File: metric3_lexical.csv
- Includes first-person pronoun frequency, past-tense verb frequency, and type-token ratio.
