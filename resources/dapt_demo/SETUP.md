# Setup Guide

Get the DAPT demo running on your computer.

---

## Prerequisites

**Required:**
- Python 3.8 or higher
- 4GB RAM minimum
- 500MB free disk space

**Optional:**
- GPU with CUDA (for faster training with larger models)
- 8GB+ RAM (for larger models)

---

## Installation Steps

### Step 1: Check Python

```bash
python --version
```

Should show Python 3.8 or higher. If not, download from [python.org](https://www.python.org/downloads/).

### Step 2: Navigate to folder

```bash
cd dapt_demo
```

### Step 3: Create virtual environment

```bash
python -m venv venv
```

### Step 4: Activate virtual environment

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 5: Install dependencies

```bash
pip install -r requirements.txt
```

This will take 2-5 minutes and download:
- `transformers` - Hugging Face library for LLMs
- `peft` - Parameter-Efficient Fine-Tuning (LoRA)
- `torch` - PyTorch deep learning framework
- `datasets` - Data loading utilities

### Step 6: Verify installation

```bash
python -c "import transformers, peft, torch; print('Success!')"
```

Should print "Success!" with no errors.

---

## Run the Demo

```bash
python adapt_model.py
```

**What happens:**
1. Downloads GPT-2 model (~500MB, first time only)
2. Loads sample medical data
3. Adapts model using LoRA
4. Shows before/after predictions
5. Saves adapted model

**Time:** 30-60 seconds on CPU, faster on GPU

---

## Troubleshooting

### "python: command not found"
Try `python3` instead of `python`

### "Module not found: transformers"
Make sure virtual environment is activated:
```bash
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
# Then reinstall
pip install -r requirements.txt
```

### "Out of memory"
The demo uses GPT-2 small (124M) which needs ~1GB RAM. If you still get errors:
- Close other programs
- Reduce batch size in `adapt_model.py` (line 158): `per_device_train_batch_size=1`

### "CUDA out of memory" (if using GPU)
Add this to the script:
```python
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Force CPU
```

### Downloads are slow
The first run downloads GPT-2 (~500MB). Be patient. Subsequent runs use cached model.

---

## What Gets Downloaded

On first run:
- GPT-2 model: ~500MB
- GPT-2 tokenizer: ~1MB

Total: ~500MB

Models are cached in:
- Windows: `C:\Users\<username>\.cache\huggingface\`
- Mac/Linux: `~/.cache/huggingface/`

---

## Testing Your Setup

After installation, test everything works:

```bash
# Test 1: Check imports
python -c "import transformers; print('Transformers:', transformers.__version__)"
python -c "import peft; print('PEFT:', peft.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__)"

# Test 2: Run the demo
python adapt_model.py
```

You should see:
- Model loading messages
- "Before adaptation" predictions
- Training progress
- "After adaptation" predictions
- "Demo Complete!"

---

## Next Steps

✅ **Setup complete!** Now:

1. Read the demo output carefully
2. Look at `sample_data/medical_texts.txt` to see the training data
3. Try Exercise 1 in EXERCISES.md
4. Experiment with your own domain data

---

## Optional: GPU Setup

If you have an NVIDIA GPU and want faster training:

### Windows

1. Install CUDA Toolkit from NVIDIA
2. Reinstall PyTorch with CUDA:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### Mac (Apple Silicon)

PyTorch supports MPS (Metal Performance Shaders):
```bash
# Check if MPS is available
python -c "import torch; print(torch.backends.mps.is_available())"
```

If True, the demo will automatically use your GPU.

### Linux

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

## Uninstalling

To remove everything:

```bash
# Deactivate virtual environment
deactivate

# Delete the folder
rm -rf dapt_demo  # Mac/Linux
rmdir /s dapt_demo  # Windows
```

To clear cached models:
```bash
# Windows
rmdir /s %USERPROFILE%\.cache\huggingface
# Mac/Linux
rm -rf ~/.cache/huggingface
```

---

## Getting Help

**Installation issues:**
1. Check Python version (`python --version`)
2. Make sure virtual environment is activated
3. Try reinstalling: `pip install --upgrade -r requirements.txt`

**Runtime errors:**
1. Read error message carefully
2. Check EXERCISES.md for common issues
3. Ask your instructor

---

## System Requirements by Model Size

| Model | Parameters | RAM | GPU VRAM | Speed (CPU) |
|-------|------------|-----|----------|-------------|
| GPT-2 | 124M | 2GB | - | 30-60s |
| GPT-2 Medium | 355M | 4GB | - | 2-3min |
| GPT-2 Large | 774M | 8GB | 4GB | 5-10min |
| LLaMA 7B | 7B | 32GB | 16GB | Hours |

**For this demo:** We use GPT-2 (124M) which works on any modern computer.

---

**Ready?** Go to [README.md](README.md) to run your first adaptation!
