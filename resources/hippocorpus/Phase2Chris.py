import os
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    TrainingArguments,
    Trainer,
)
from peft import LoraConfig, get_peft_model

MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

BASE_DIR = Path(__file__).resolve().parent
TRAIN_FILE = BASE_DIR / "train_recalled.jsonl"
VAL_FILE = BASE_DIR / "val_recalled.jsonl"
OUTPUT_DIR = BASE_DIR / "lora_tinyllama_hippo"

MAX_LEN = 256
EPOCHS = 3
LR = 2e-4
BATCH = 1
WARMUP_STEPS = 50


def main():
    print("BASE_DIR =", BASE_DIR)
    print("TRAIN_FILE =", TRAIN_FILE)
    print("VAL_FILE =", VAL_FILE)
    print("TRAIN exists?", TRAIN_FILE.exists())
    print("VAL exists?", VAL_FILE.exists())

    if not TRAIN_FILE.exists():
        raise FileNotFoundError(f"Could not find training file: {TRAIN_FILE}")
    if not VAL_FILE.exists():
        raise FileNotFoundError(f"Could not find validation file: {VAL_FILE}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    raw = load_dataset(
        "json",
        data_files={
            "train": str(TRAIN_FILE),
            "validation": str(VAL_FILE),
        },
    )

    def tokenize(batch):
        return tokenizer(
            batch["story"],
            truncation=True,
            max_length=MAX_LEN,
        )

    tok = raw.map(tokenize, batched=True, remove_columns=["story"])

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    if torch.cuda.is_available():
        model_dtype = torch.float16
        device_map = "auto"
    else:
        model_dtype = torch.float32
        device_map = None

    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=model_dtype,
        device_map=device_map,
    )

    base_model.gradient_checkpointing_enable()
    base_model.config.use_cache = False

    print("\nChecking module names for LoRA targets...")
    found = set()
    for name, _ in base_model.named_modules():
        if name.endswith(("q_proj", "k_proj", "v_proj", "o_proj")):
            found.add(name.split(".")[-1])
    print("Found projection suffixes:", sorted(found))

    lora_cfg = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(base_model, lora_cfg)
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=BATCH,
        per_device_eval_batch_size=BATCH,
        learning_rate=LR,
        warmup_steps=WARMUP_STEPS,
        lr_scheduler_type="cosine",
        logging_steps=25,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        report_to="none",
        bf16=False,
        fp16=False,
        dataloader_pin_memory=False
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=tok["train"],
        eval_dataset=tok["validation"],
        data_collator=data_collator,
    )

    trainer.train()

    save_path = OUTPUT_DIR / "final_adapter"
    trainer.model.save_pretrained(str(save_path))
    tokenizer.save_pretrained(str(save_path))

    print(f"\nSaved LoRA adapter to: {save_path}")


if __name__ == "__main__":
    main()
