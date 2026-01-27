# Domain Adaptation Pre-Training (DAPT) Demo

> Adapt a language model to your domain using your own data

## What This Does

This demo teaches you to adapt a pre-trained language model (LLM) to a specific domain using DAPT + LoRA:
- **DAPT**: Continue pre-training on domain-specific text
- **LoRA**: Efficient fine-tuning (updates <1% of parameters)
- **Your Data**: Use any text data from your domain

**Cost:** $0 (runs on your CPU, no GPUs needed for this tiny demo)

---

## Quick Start

### 1. Install (2 minutes)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt
```

### 2. Run Demo (30 seconds)

```bash
python adapt_model.py
```

This will:
1. Load a tiny language model (GPT-2 small, 124M params)
2. Adapt it to medical domain using sample data
3. Show before/after predictions
4. Save the adapted model

### 3. See Results

The script shows:
- **Before adaptation**: Generic responses
- **After adaptation**: Domain-specific responses
- **Model saved**: `./adapted_model/`

---

## What You'll Learn

1. ✅ How to format domain-specific text data
2. ✅ How to use LoRA for efficient adaptation
3. ✅ How to continue pre-training on your data
4. ✅ How to evaluate adaptation success
5. ✅ How to save and load adapted models

---

## Data Format

Your data should be plain text files, one document per line (or paragraph):

```
sample_data/
├── medical_texts.txt      # Domain-specific text
└── law_texts.txt          # Another domain example
```

**Example line:**
```
The patient presented with acute myocardial infarction and elevated troponin levels.
```

That's it! No special formatting needed.

---

## What's Included

| File | Purpose |
|------|---------|
| `adapt_model.py` | Main adaptation script |
| `requirements.txt` | Python packages |
| `sample_data/` | Example domain data |
| `EXERCISES.md` | 5 hands-on exercises |
| `SETUP.md` | Detailed installation |

---

## Full Documentation

- **[SETUP.md](SETUP.md)** - Complete installation guide
- **[EXERCISES.md](EXERCISES.md)** - 5 student exercises
- **[TEACHING_GUIDE.md](TEACHING_GUIDE.md)** - For instructors

---

## Important Notes

⚠️ **This is a TOY DEMO**
- Uses tiny model (GPT-2 small, 124M)
- Uses tiny dataset (50 examples)
- Trains for 1 epoch
- Meant for learning, not production

✅ **For Real Adaptation:**
- Use larger models (7B+)
- Use more data (1000+ examples)
- Train for multiple epochs
- Use GPUs for faster training
- See EXERCISES.md for guidance

---

## Requirements

- Python 3.8+
- 4GB RAM
- No GPU needed (for demo)
- ~500MB disk space

---

## Next Steps

1. Run the demo: `python adapt_model.py`
2. Try Exercise 1: Adapt to your own domain
3. Read EXERCISES.md for more challenges

---

**Made for students learning domain adaptation** • Free & open-source
