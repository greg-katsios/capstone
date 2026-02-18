# Exercise: Domain Adaptation with Autobiographical Narratives

## Overview

In the demo, you adapted GPT-2 (124M parameters) to medical text using LoRA. Now you'll do it for real: adapt a modern 1B-parameter language model to **autobiographical narrative style** using data from the HippoCorpus dataset, then measure whether the adaptation actually worked.

The goal of this exercise is for you to **run a real ML experiment end-to-end** and learn from the results. You are not expected to be an expert in every library involved. What matters is that you understand what you're doing at each stage, why you're doing it, and what the results mean.

## A Note on Using AI Tools

You will use AI assistance at different levels depending on the phase. This is intentional. Some parts of this exercise are about building genuine understanding, you need to get your hands dirty. Other parts involve specialized implementation details where getting stuck on syntax would waste your time without teaching you anything new. Here's the breakdown:

| Phase | AI Policy | Why |
|---|---|---|
| Data exploration | **Write your own code.** | You need to actually look at this data. |
| Training | **Hybrid.** Read the docs yourself, use AI to troubleshoot. | Understanding HuggingFace's ecosystem is a real skill. |
| Evaluation | **AI-assisted implementation is fine.** | Focus on understanding the metrics, not reimplementing them. |

More detail on each below.

---

## Phase 1: Data Preparation (Write Your Own Code)

Download the HippoCorpus dataset from `https://msropendata.com/datasets/0a83fb6f-a759-4a17-aaa2-fbac84577318` (also on HuggingFace at `allenai/hippocorpus`, though it requires manual download). The CSV contains 6,854 diary-like stories in three categories: recalled, imagined, and retold.

**Do this yourself, without AI.** Load the CSV. Explore it. Write your own pandas code to answer:

- How many stories are in each `memType` category?
- What is the average story length (in words) for recalled vs. imagined?
- Read 5–10 recalled stories. What do they actually sound like? What makes them feel "autobiographical"?
- Are there any empty rows, duplicates, or obvious data quality issues?

Then filter to only `recalled` stories, extract the `story` column, and split 90/10 into train and validation sets.

**Why no AI here:** If you don't know what's in your data, nothing downstream will make sense to you. You cannot interpret evaluation results for a dataset you've never read.

---

## Phase 2: Training (Hybrid Approach)

Use a 1–1.5B parameter model. Good choices: `TinyLlama/TinyLlama-1.1B-Chat-v1.0` (1.1B, Llama 2 architecture), `Qwen/Qwen2.5-1.5B`, or `Qwen/Qwen2.5-1.5B-Instruct`.

**What you should do yourself:**
- Read the model card on HuggingFace for whatever model you pick. Understand what it was trained on and how big it is.
- Read the PEFT/LoRA documentation enough to understand what `r`, `lora_alpha`, and `target_modules` mean. Don't just copy values.
- Look at your chosen model's architecture (`model.named_modules()`) to identify the correct attention layer names for `target_modules`. This is a 2-minute exercise that teaches you something real.
- Understand what `TrainingArguments` parameters you're setting and why (learning rate, epochs, batch size, scheduler).

**Where AI can help:**
- Debugging tokenizer issues (padding tokens, special tokens, chat templates) — these are genuinely fiddly and model-specific.
- Resolving CUDA out-of-memory errors, gradient checkpointing setup, or dtype configuration.
- Syntax for loading the dataset into the HuggingFace `Dataset` format if you're unfamiliar with the library.

**Suggested hyperparameters:** 3 epochs, batch size 4, learning rate 2e-4, cosine schedule with 50 warmup steps, LoRA rank 16, alpha 32. If you run out of memory, reduce batch size to 2 with gradient accumulation of 2. Log your training loss.

**Why hybrid:** HuggingFace Transformers + PEFT is the standard stack you'll use in industry. You should build real familiarity with it. But there's no learning value in spending 2 hours debugging a padding token mismatch; ask AI and move on.

---

## Phase 3: Evaluation (AI-Assisted Implementation)

This is where the experiment pays off. Compare the base model against your adapted model using three metrics. **You should understand what each metric measures and what the results mean.** The implementation code itself can come from AI.

### Metric 1: Perplexity (primary)
Compute perplexity on your held-out validation stories for both the base model and the adapted model. Lower perplexity after adaptation means the model has learned to better predict autobiographical language patterns.

*Understand:* What perplexity actually measures (exponentiated average negative log-likelihood). Why lower is better. What a "good" drop looks like vs. a trivial one.

### Metric 2: Narrative Generation Quality (qualitative)
Give both models the same 5 story-opening prompts (e.g., *"I remember the day when"*, *"That summer my family"*, *"The hardest thing I ever"*). Generate 150 tokens from each. Rate the outputs yourself on a 1–5 scale for:
- **Emotional specificity** does it name real feelings, or stay vague?
- **Temporal grounding** does it reference concrete times, places, people?
- **First-person consistency** does it stay in the narrator's voice?

### Metric 3: Lexical Analysis (quantitative)
Using NLTK or spaCy, compare the generated outputs on: (a) frequency of first-person pronouns (I/my/me/we), (b) frequency of past-tense verbs, and (c) type-token ratio. Autobiographical text should show higher rates of first-person pronouns and past tense after adaptation.

**Why AI is fine here:** The value is in interpreting the results, does the perplexity drop confirm what you see qualitatively? Do the lexical shifts match what you'd expect from reading the training data? That's the thinking that matters. Writing a POS-tagger from scratch is not.

---

## Deliverable

A short writeup (1–2 pages) with:
- Your perplexity table (before vs. after)
- Side-by-side comparison of 2–3 generated samples with your qualitative ratings
- Lexical analysis results (a small table or chart is fine)
- A paragraph reflecting on: What changed? What didn't? Did the metrics agree with each other? What would you do differently with more time or compute?

Include your modified training script.
