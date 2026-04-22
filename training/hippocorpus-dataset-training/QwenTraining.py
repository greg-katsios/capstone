import os
import re
import pandas as pd
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


# --------------------
# Config
# --------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_MODEL = "Qwen/Qwen3-0.6B"
CSV_PATH = os.path.join(SCRIPT_DIR, "hcV3-stories.csv")
OUT_DIR = os.path.join(SCRIPT_DIR, "Qwen3-0.6B_hippo_recalled_lora_mps")

SEED = 42
MAX_LEN = 256

# CPU/MPS speed knobs
NUM_EPOCHS = 2
ENABLE_EVAL = False
SAVE_STRATEGY = "epoch"
DATALOADER_WORKERS = max(1, min(4, (os.cpu_count() or 1) - 1))


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()


def main():
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    # 1) Load recalled data
    df = pd.read_csv(CSV_PATH)
    df = df[df["memType"] == "recalled"].copy()
    df["story"] = df["story"].astype(str).map(clean_text)
    df = df[df["story"].str.len() > 0]

    ds = Dataset.from_pandas(df[["story"]], preserve_index=False).shuffle(seed=SEED)
    if ENABLE_EVAL:
        split = ds.train_test_split(test_size=0.1, seed=SEED)
        train_ds, val_ds = split["train"], split["test"]
    else:
        train_ds, val_ds = ds, None

    # 2) Tokenizer
    tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    def tokenize(batch):
        return tok(batch["story"], truncation=True, max_length=MAX_LEN, padding=False)

    train_tok = train_ds.map(tokenize, batched=True, remove_columns=["story"])
    val_tok = val_ds.map(tokenize, batched=True, remove_columns=["story"]) if val_ds is not None else None

    # 3) Model
    use_mps = torch.backends.mps.is_available()
    device = torch.device("mps") if use_mps else torch.device("cpu")
    print("Using device:", device)

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16 if use_mps else torch.float32,
        low_cpu_mem_usage=True,
    )
    model.to(device)

    # 4) LoRA (Qwen attention projection layers)
    lora_cfg = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],
        bias="none",
    )

    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    # 5) Train
    collator = DataCollatorForLanguageModeling(tok, mlm=False)

    args = TrainingArguments(
        output_dir=OUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_steps=10,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=2,
        per_device_eval_batch_size=1,
        logging_steps=50,
        eval_strategy="no" if not ENABLE_EVAL else "epoch",
        save_strategy=SAVE_STRATEGY,
        save_total_limit=2,
        dataloader_num_workers=DATALOADER_WORKERS,
        report_to="none",
        fp16=False,
        bf16=False,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_tok,
        eval_dataset=val_tok,
        data_collator=collator,
    )

    trainer.train()

    # 6) Save adapter
    os.makedirs(OUT_DIR, exist_ok=True)
    model.save_pretrained(OUT_DIR)
    tok.save_pretrained(OUT_DIR)

    print("Qwen training complete.")
    print("Adapter saved to:", os.path.abspath(OUT_DIR))
    print("Look for:", os.path.join(OUT_DIR, "adapter_config.json"))


if __name__ == "__main__":
    main()
