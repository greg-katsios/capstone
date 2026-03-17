# train.py
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType
import pandas as pd
from datasets import Dataset

# ── 1. Load tokenizer ──────────────────────────────────────────────────────────
# Qwen2.5-Instruct uses a specific chat template. The tokenizer handles this.
# We need to set a pad token because Qwen's tokenizer doesn't have one by default
# (it's a decoder-only model trained without padding).
tokenizer = AutoTokenizer.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    trust_remote_code=True,
)
tokenizer.pad_token = tokenizer.eos_token  # common fix for decoder-only models
tokenizer.padding_side = "right"           # pad on right for causal LM training


# ── 2. Load base model ─────────────────────────────────────────────────────────
# bfloat16 halves memory usage vs float32. Fine for modern GPUs (Ampere+).
# If you get dtype errors on older hardware, switch to float16 or remove it.
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("Using device:", device)

model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    dtype=torch.float32,
).to("mps")

# ── 3. Configure LoRA ──────────────────────────────────────────────────────────
# YOU should have confirmed these target_modules by running model.named_modules()
# r=16 means each LoRA adapter is a pair of matrices: (hidden_dim x 16) and (16 x hidden_dim)
# lora_alpha=32 is the scaling factor: effective_lr = lora_alpha / r = 2.0
# lora_dropout adds regularization to the adapter layers
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # verify these yourself!
    lora_dropout=0.05,
    bias="none",
)

model = get_peft_model(model, lora_config)   # apply LoRA first
model = model.to(device)                     # THEN move to MPS
model.print_trainable_parameters()  # should show ~1-2% of total params are trainable


# ── 4. Prepare your dataset ────────────────────────────────────────────────────
# Replace this with your actual data. Each item should be a formatted string
# that matches the chat template Qwen2.5-Instruct expects.
# See the model card for the exact format: <|im_start|>user\n...<|im_end|>\n etc.

def format_example(example):
    """Format a single example using Qwen's chat template."""
    messages = [
        {"role": "user", "content": example["instruction"]},
        {"role": "assistant", "content": example["output"]},
    ]
    # apply_chat_template handles the special tokens (<|im_start|>, etc.) for you
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )

# Load your saved splits
train_df = pd.read_csv('hippocorpus_exercise/train.csv')
test_df = pd.read_csv('hippocorpus_exercise/test.csv')

# The column is called 'story' — rename to 'text' for clarity (optional)
train_df = train_df.rename(columns={'story': 'text'})
test_df = test_df.rename(columns={'story': 'text'})

# Convert to HuggingFace Dataset format
train_dataset = Dataset.from_pandas(train_df[['text']])
test_dataset = Dataset.from_pandas(test_df[['text']])

def tokenize(example):
    tokens = tokenizer(
        example["text"],          # ← directly use the text column
        truncation=True,
        max_length=256,
        padding="max_length",
    )
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens
# dataset = Dataset.from_list(raw_data).map(tokenize, remove_columns=["instruction", "output"])

train_dataset = train_dataset.map(tokenize, remove_columns=["text"])
test_dataset = test_dataset.map(tokenize, remove_columns=["text"])

train_dataset = train_dataset.select(range(500))   # ~1/5 of the data
test_dataset = test_dataset.select(range(50))


# ── 5. Training arguments ──────────────────────────────────────────────────────
# Each argument here has a reason:
# - learning_rate: 2e-4 is standard for LoRA (higher than full fine-tuning because adapters are small)
# - cosine schedule: smoothly decays LR, better than linear for short runs
# - warmup_steps: avoids large gradient updates at the start when model is "cold"
# - gradient_checkpointing: trades compute for memory (recomputes activations on backward pass)
training_args = TrainingArguments(
    output_dir="./llama-lora-output",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=2,
    dataloader_pin_memory=False,
    learning_rate=2e-4,
    lr_scheduler_type="cosine",
    warmup_steps=50,
    logging_steps=10,
    save_strategy="epoch",
    bf16=False,           # ← MPS doesn't support bf16 training
    fp16=False,           # ← also leave this off; MPS uses float32
    gradient_checkpointing=False,   # ← can be buggy on MPS, disable for now
    dataloader_num_workers=0,       # ← add this, fixes MPS dataloader deadlock
    report_to="none",
    eval_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

print("Model device:", next(model.parameters()).device)
print("MPS available:", torch.backends.mps.is_available())

# Verify one manual training step works before handing off to Trainer
model.train()
batch = next(iter(trainer.get_train_dataloader()))
batch = {k: v.to("mps") for k, v in batch.items()}
outputs = model(**batch)
print("Loss:", outputs.loss.item())   # if this prints, backward pass works
outputs.loss.backward()
print("Backward pass complete")

trainer.train()
model.save_pretrained("./llama-lora-final")