# Requirements:
#   - transformers
#   - datasets
#   - torch-directml (python 3.12 or lower) (optional, for AMD GPU support on Windows)

import os
import re
import importlib
import pandas as pd
import torch

try:
    torch_directml = importlib.import_module("torch_directml")
except ImportError:
    torch_directml = None

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
BASE_MODEL = "Qwen/Qwen3-1.7B"
CSV_PATH = os.path.join(SCRIPT_DIR, "hcV3-stories.csv")
OUT_DIR = os.path.join(SCRIPT_DIR, "Qwen3-1.7B_hippo_recalled_lora_mps")

SEED = 42
MAX_LEN = 256

# CPU/MPS speed knobs
NUM_EPOCHS = 2
ENABLE_EVAL = False
SAVE_STRATEGY = "epoch"
DATALOADER_WORKERS = max(1, min(4, (os.cpu_count() or 1) - 1))


def clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", str(s)).strip()


class DebugTrainer(Trainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._printed_first_batch = False
        self._printed_first_batch_prepared = False

    def _prepare_inputs(self, inputs):
        inputs = super()._prepare_inputs(inputs)
        target_device = next(self.model.parameters()).device
        prepared_inputs = {
            name: value.to(target_device) if torch.is_tensor(value) else value
            for name, value in inputs.items()
        }
        if not self._printed_first_batch_prepared:
            tensor_devices = {
                name: value.device
                for name, value in prepared_inputs.items()
                if torch.is_tensor(value)
            }
            print(f"Prepared first batch tensor devices: {tensor_devices}")
            self._printed_first_batch_prepared = True
        return prepared_inputs

    def training_step(self, model, inputs, num_items_in_batch=None):
        if not self._printed_first_batch:
            tensor_devices = {
                name: value.device
                for name, value in inputs.items()
                if torch.is_tensor(value)
            }
            print(f"Raw first batch tensor devices: {tensor_devices}")
            self._printed_first_batch = True
        return super().training_step(model, inputs, num_items_in_batch=num_items_in_batch)


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
    use_cuda = torch.cuda.is_available()
    use_mps = torch.backends.mps.is_available()
    use_directml = torch_directml is not None

    if use_cuda:
        backend = "CUDA"
        device = torch.device("cuda")
        model_dtype = torch.float16
    elif use_mps:
        backend = "MPS"
        device = torch.device("mps")
        model_dtype = torch.float16
    elif use_directml:
        backend = "DirectML"
        device = torch_directml.device()
        # DirectML float16 support can vary by op/hardware; float32 is safer.
        model_dtype = torch.float32
    else:
        backend = "CPU"
        device = torch.device("cpu")
        model_dtype = torch.float32

    print(f"Using backend: {backend} ({device})")
    if backend == "CPU":
        print(
            "CPU fallback reason: CUDA unavailable, MPS unavailable, and torch-directml not installed."
        )
        print("Install torch-directml on Windows+AMD, or use Linux ROCm for best AMD training support.")

    model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        dtype=model_dtype,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )

    model = model.to(device)
    print(f"Model first parameter device: {next(model.parameters()).device}")

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
    model.gradient_checkpointing_enable()
    model.print_trainable_parameters()

    # 5) Train
    collator = DataCollatorForLanguageModeling(tok, mlm=False)

    args = TrainingArguments(
        output_dir=OUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=2e-4,
        lr_scheduler_type="cosine",
        warmup_steps=10,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
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

    trainer = DebugTrainer(
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
