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
BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
CSV_PATH = os.path.join(SCRIPT_DIR, "hcV3-stories.csv")  # UPDATED: path works from any cwd
OUT_DIR = os.path.join(SCRIPT_DIR, "tinyllama_1p1b_hippo_recalled_lora_mps")  # UPDATED: keep outputs with script

SEED = 42
MAX_LEN = 256  # UPDATED: shorter sequences significantly reduce CPU training time

# UPDATED: CPU-focused speed knobs
NUM_EPOCHS = 2                 # fewer passes over data = faster wall-clock training
ENABLE_EVAL = False            # disable eval during training for maximum speed
SAVE_STRATEGY = "epoch"        # checkpoint once per epoch instead of frequent step saves
DATALOADER_WORKERS = max(1, min(4, (os.cpu_count() or 1) - 1))  # cap workers to avoid CPU oversubscription


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()


def main():
    # UPDATED: use all available CPU threads for faster matmul/attention kernels on CPU-only systems.
    torch.set_num_threads(max(1, os.cpu_count() or 1))

    # --------------------
    # 1) Load recalled data + split 90/10
    # --------------------
    df = pd.read_csv(CSV_PATH)
    df = df[df["memType"] == "recalled"].copy()
    df["story"] = df["story"].astype(str).map(clean_text)
    df = df[df["story"].str.len() > 0]

    ds = Dataset.from_pandas(df[["story"]], preserve_index=False).shuffle(seed=SEED)
    if ENABLE_EVAL:
        split = ds.train_test_split(test_size=0.1, seed=SEED)
        train_ds, val_ds = split["train"], split["test"]
    else:
        train_ds, val_ds = ds, None  # UPDATED: skip val split preprocessing when eval is disabled

    # --------------------
    # 2) Tokenizer
    # --------------------
    tok = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    def tokenize(batch):
        return tok(batch["story"], truncation=True, max_length=MAX_LEN, padding=False)

    train_tok = train_ds.map(tokenize, batched=True, remove_columns=["story"])
    val_tok = val_ds.map(tokenize, batched=True, remove_columns=["story"]) if val_ds is not None else None

    # --------------------
    # 3) Load model on MPS (no bitsandbytes on Mac)
    # --------------------
    use_mps = torch.backends.mps.is_available()
    device = torch.device("mps") if use_mps else torch.device("cpu")
    print("Using device:", device)

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        torch_dtype=torch.float16 if use_mps else torch.float32,
        low_cpu_mem_usage=True,  # UPDATED: lowers peak RAM and can speed model load on CPU
    )
    model.to(device)

    # --------------------
    # 4) LoRA (TinyLlama is Llama-style: q/k/v/o proj usually exist)
    # --------------------
    lora_cfg = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,                      # UPDATED: fewer LoRA params -> faster backward pass
        lora_alpha=16,            # UPDATED: keep alpha proportional to rank
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj"],  # UPDATED: adapt fewer modules for speed
        bias="none",
    )

    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    # --------------------
    # 5) Train (small batch for M2)
    # --------------------
    collator = DataCollatorForLanguageModeling(tok, mlm=False)

    args = TrainingArguments(
        output_dir=OUT_DIR,
        num_train_epochs=NUM_EPOCHS,  # UPDATED: faster by reducing epochs
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_steps=10,               # UPDATED: shorter warmup for shorter runs

        per_device_train_batch_size=2,      # UPDATED: often better CPU throughput than micro-batch=1
        gradient_accumulation_steps=2,      # UPDATED: keeps effective batch near prior setting
        per_device_eval_batch_size=1,

        logging_steps=50,                   # UPDATED: less logging overhead
        eval_strategy="no" if not ENABLE_EVAL else "epoch",  # UPDATED: disable eval for speed
        save_strategy=SAVE_STRATEGY,        # UPDATED: less frequent checkpointing
        save_total_limit=2,
        dataloader_num_workers=DATALOADER_WORKERS,  # UPDATED: parallelize data loading on CPU

        report_to="none",

        # Important on MPS: Trainer fp16 flags can be finicky; leave them off.
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

    # --------------------
    # 6) Save adapter (what Phase 3 loads)
    # --------------------
    os.makedirs(OUT_DIR, exist_ok=True)
    model.save_pretrained(OUT_DIR)   # produces adapter_config.json
    tok.save_pretrained(OUT_DIR)

    print("Phase 2 complete.")
    print("Adapter saved to:", os.path.abspath(OUT_DIR))
    print("Look for:", os.path.join(OUT_DIR, "adapter_config.json"))


if __name__ == "__main__":
    main()