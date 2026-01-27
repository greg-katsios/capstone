# Student Exercises

Learn domain adaptation through hands-on practice.

---

## Exercise 1: Adapt to Your Own Domain (60 minutes)

**Goal:** Collect domain-specific data and adapt the model

### Steps

1. **Choose a domain** you're interested in:
   - Academic field (psychology, economics, biology)
   - Industry (finance, healthcare, legal)
   - Hobby (cooking, gaming, sports)

2. **Collect 50-100 text examples:**
   - Wikipedia articles in your domain
   - Academic paper abstracts
   - News articles
   - Blog posts
   - Textbook passages

3. **Format your data:**
   - Create `sample_data/my_domain.txt`
   - One example per line
   - Plain text, no special formatting

   Example:
   ```
   In behavioral economics, loss aversion describes how people fear losses more than equivalent gains.
   The prisoner's dilemma illustrates how rational individuals might not cooperate even when beneficial.
   Prospect theory challenges expected utility theory by showing asymmetric value functions for gains and losses.
   ```

4. **Modify `adapt_model.py`:**
   - Line 39: Change `DATA_PATH = "sample_data/my_domain.txt"`
   - Run: `python adapt_model.py`

5. **Test the adaptation:**
   - Create domain-specific test prompts
   - Compare before/after predictions
   - Does the model use domain terminology?

### Questions to Answer

1. What domain did you choose and why?
2. How many examples did you collect?
3. Did the model's predictions improve? How?
4. What domain-specific terms appear in adapted output?

### Deliverable

1-page report with:
- Domain description
- Example training texts (3-5)
- Before/after predictions comparison
- Analysis of improvement

---

## Exercise 2: LoRA Configuration Experiment (45 minutes)

**Goal:** Understand how LoRA hyperparameters affect adaptation

### Background

LoRA has key hyperparameters:
- **r** (rank): Higher = more parameters, better adaptation, slower
- **alpha**: Scaling factor (typically 2x the rank)
- **dropout**: Regularization (0.0-0.2)

### Steps

1. **Baseline:** Run with default settings (r=8, alpha=16)

2. **Low rank:** Change to r=4, alpha=8
   - Line 43: `LORA_R = 4`
   - Line 44: `LORA_ALPHA = 8`

3. **High rank:** Change to r=16, alpha=32
   - Line 43: `LORA_R = 16`
   - Line 44: `LORA_ALPHA = 32`

4. **For each configuration:**
   - Count trainable parameters (shown during run)
   - Time the training
   - Test with same prompts
   - Save outputs

### Questions to Answer

1. How did trainable parameters change with rank?
2. Which configuration gave best results? Why?
3. What's the tradeoff between rank and speed?
4. When would you use low vs high rank?

### Deliverable

Comparison table:
| Config | r | Trainable Params | Time | Quality Score |
|--------|---|------------------|------|---------------|
| Low    | 4 | X | Xs | 3/5 |
| Default| 8 | Y | Ys | 4/5 |
| High   | 16| Z | Zs | 5/5 |

+ 1-page analysis

---

## Exercise 3: Compare Multiple Domains (90 minutes)

**Goal:** See how domain affects adaptation

### Steps

1. **Prepare 3 domain datasets:**
   - Medical (provided)
   - Law (provided)
   - Your choice (collect your own)

2. **For each domain:**
   - Adapt model: `python adapt_model.py` (change DATA_PATH)
   - Save to different folder (change OUTPUT_DIR)
   - Test with domain-specific prompts

3. **Cross-domain testing:**
   - Test medical model on legal prompts
   - Test legal model on medical prompts
   - Does specialization help or hurt?

4. **Measure domain specificity:**
   - Count domain-specific terms in output
   - Rate coherence (1-5)
   - Note any hallucinations

### Questions to Answer

1. Which domain adapted most successfully?
2. Does a medical-adapted model work on law text?
3. What happens when domains are too different?
4. Is it better to have general or specialized model?

### Deliverable

3-page report with:
- Training data description for each domain
- Prediction examples from each model
- Cross-domain test results
- Analysis and conclusions

---

## Exercise 4: Evaluation Metrics (60 minutes)

**Goal:** Quantify adaptation success

### Steps

1. **Prepare test set:**
   - Collect 20 examples from your domain (separate from training)
   - Save as `sample_data/test_set.txt`

2. **Calculate perplexity:**

   Add this to `adapt_model.py`:
   ```python
   from transformers import pipeline
   import math

   def calculate_perplexity(model, tokenizer, texts):
       total_loss = 0
       for text in texts:
           inputs = tokenizer(text, return_tensors="pt")
           with torch.no_grad():
               outputs = model(**inputs, labels=inputs["input_ids"])
               total_loss += outputs.loss.item()
       return math.exp(total_loss / len(texts))
   ```

3. **Measure before and after:**
   - Base model perplexity on test set
   - Adapted model perplexity on test set
   - Lower perplexity = better

4. **Calculate improvement:**
   - Perplexity reduction %
   - Statistical significance?

### Questions to Answer

1. What was the perplexity before adaptation?
2. What was the perplexity after adaptation?
3. What % improvement did you achieve?
4. Does lower perplexity mean better model?

### Deliverable

Technical report with:
- Methodology description
- Perplexity calculations
- Improvement statistics
- Discussion of limitations

---

## Exercise 5: Production-Ready Adaptation (120 minutes)

**Goal:** Create a real, usable adapted model

### Requirements

- Larger dataset (500+ examples)
- Multiple epochs (3-5)
- Validation set
- Proper evaluation
- Documentation

### Steps

1. **Data collection:**
   - 500+ training examples
   - 100 validation examples
   - 50 test examples

2. **Modify training config:**
   ```python
   training_args = TrainingArguments(
       num_train_epochs=3,
       per_device_train_batch_size=4,
       evaluation_strategy="steps",
       eval_steps=50,
       save_strategy="steps",
       save_steps=100,
       load_best_model_at_end=True,
   )
   ```

3. **Add validation:**
   - Split data into train/val
   - Monitor validation loss
   - Use early stopping if available

4. **Document everything:**
   - Data sources
   - Preprocessing steps
   - Training configuration
   - Evaluation results
   - Usage instructions

### Deliverable

Complete project with:
- All data files
- Modified script
- README explaining the model
- Evaluation report
- Usage examples

---

## Grading Rubric

| Category | Points | What to Look For |
|----------|--------|------------------|
| **Data Quality** | 30% | Appropriate domain, clean formatting |
| **Technical Execution** | 30% | Code runs, correct configuration |
| **Analysis** | 25% | Thoughtful interpretation of results |
| **Documentation** | 15% | Clear writing, proper citations |

---

## Tips for Success

✅ **Do:**
- Start with small experiments
- Document everything as you go
- Compare before/after carefully
- Think about why changes occur
- Ask questions when stuck

❌ **Don't:**
- Use too little data (<50 examples)
- Skip the analysis
- Ignore negative results (they're valuable!)
- Copy outputs without understanding
- Forget to save your work

---

## Common Issues

**"Model quality didn't improve"**
- Need more training data
- Try higher LoRA rank
- Train for more epochs
- Check data quality

**"Training is too slow"**
- Reduce batch size
- Use smaller model
- Use GPU if available
- Reduce number of epochs for testing

**"Can't collect enough data"**
- Use data augmentation
- Combine multiple sources
- Focus on quality over quantity
- Consider using existing datasets

---

## Advanced Extensions

For students who finish early:

1. **Multi-domain adaptation:** Adapt to multiple domains simultaneously
2. **Incremental adaptation:** Adapt → evaluate → collect more data → re-adapt
3. **Comparison study:** LoRA vs full fine-tuning vs prompt engineering
4. **Domain transfer:** Train on domain A, test on related domain B
5. **Ensemble methods:** Combine multiple adapted models

---

## Resources

- [Hugging Face PEFT Documentation](https://huggingface.co/docs/peft)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [DAPT Guide](https://marutitech.com/domain-adaptive-pretraining-llms/)
- [Transformers Documentation](https://huggingface.co/docs/transformers)

---

**Need help?** Check SETUP.md for troubleshooting or ask your instructor!
