#!/usr/bin/env python3
"""
Domain Adaptation Pre-Training (DAPT) Demo

This script demonstrates how to adapt a pre-trained language model
to a specific domain using LoRA (Low-Rank Adaptation).

Simple, educational example for students.
"""

import os
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
import warnings
warnings.filterwarnings('ignore')


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def load_domain_data(data_path):
    """
    Load domain-specific text data from a file.

    Args:
        data_path: Path to text file (one example per line)

    Returns:
        Dataset object
    """
    print(f"Loading data from: {data_path}")

    # Load the text file
    dataset = load_dataset('text', data_files={'train': data_path})

    print(f"Loaded {len(dataset['train'])} examples")
    print(f"Sample text: {dataset['train'][0]['text'][:100]}...")

    return dataset['train']


def tokenize_function(examples, tokenizer, max_length=128):
    """Tokenize the text examples."""
    return tokenizer(
        examples['text'],
        truncation=True,
        max_length=max_length,
        padding='max_length'
    )


def test_model(model, tokenizer, prompt, max_length=50):
    """
    Test the model with a prompt and return the generated text.

    Args:
        model: The language model
        tokenizer: The tokenizer
        prompt: Input text prompt
        max_length: Maximum tokens to generate

    Returns:
        Generated text
    """
    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def main():
    """Main execution function."""

    print_section("DAPT Demo: Domain Adaptation with LoRA")

    # Configuration
    MODEL_NAME = "gpt2"  # Small model for demo (124M parameters)
    DATA_PATH = "sample_data/my_domain.txt"
    OUTPUT_DIR = "./adapted_model"

    # LoRA configuration
    LORA_R = 8  # Rank of the low-rank matrices
    LORA_ALPHA = 16  # Scaling factor
    LORA_DROPOUT = 0.1

    print(f"\nModel: {MODEL_NAME}")
    print(f"Data: {DATA_PATH}")
    print(f"LoRA rank: {LORA_R}")

    # Step 1: Load Model and Tokenizer
    print_section("Step 1: Loading Base Model")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    base_model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        dtype=torch.float32,
        device_map="cpu"  # Run on CPU for compatibility
    )

    print(f"Base model loaded: {MODEL_NAME}")
    print(f"Total parameters: {base_model.num_parameters():,}")

    # Step 2: Test Before Adaptation
    print_section("Step 2: Testing BEFORE Adaptation")

    test_prompts = [
        "League of Legends is most known for",
        "Pink wards should typically be placed in or around",
        "Tank champions should play"
    ]

    print("\nBase model predictions:")
    for prompt in test_prompts:
        result = test_model(base_model, tokenizer, prompt)
        print(f"\nPrompt: '{prompt}'")
        print(f"Output: {result}")

    # Step 3: Setup LoRA
    print_section("Step 3: Configuring LoRA")

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=["c_attn"],  # GPT-2 attention modules
        bias="none"
    )

    model = get_peft_model(base_model, lora_config)

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())

    print(f"\nTotal parameters: {total_params:,}")
    print(f"Trainable parameters: {trainable_params:,}")
    print(f"Trainable %: {100 * trainable_params / total_params:.2f}%")

    # Step 4: Load and Prepare Data
    print_section("Step 4: Preparing Domain Data")

    if not os.path.exists(DATA_PATH):
        print(f"ERROR: Data file not found: {DATA_PATH}")
        print("Please make sure sample_data/medical_texts.txt exists")
        return

    dataset = load_domain_data(DATA_PATH)

    # Tokenize dataset
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=dataset.column_names
    )

    # Data collator for language modeling
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # Causal LM, not masked LM
    )

    # Step 5: Training
    print_section("Step 5: Adapting to Domain")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=1,  # Just 1 epoch for demo
        per_device_train_batch_size=2,
        save_steps=100,
        save_total_limit=1,
        logging_steps=5,
        learning_rate=3e-4,
        warmup_steps=10,
        report_to="none",  # Don't send to wandb, etc.
        use_cpu=True  # Force CPU for compatibility
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )

    print("\nStarting adaptation...")
    print("(This will take 30-60 seconds on CPU)")

    trainer.train()

    print("\n[OK] Adaptation complete!")

    # Step 6: Test After Adaptation
    print_section("Step 6: Testing AFTER Adaptation")

    print("\nAdapted model predictions:")
    for prompt in test_prompts:
        result = test_model(model, tokenizer, prompt)
        print(f"\nPrompt: '{prompt}'")
        print(f"Output: {result}")

    # Step 7: Save Model
    print_section("Step 7: Saving Adapted Model")

    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print(f"\n[OK] Model saved to: {OUTPUT_DIR}")
    print(f"\nTo load later:")
    print(f"  from peft import AutoPeftModelForCausalLM")
    print(f"  model = AutoPeftModelForCausalLM.from_pretrained('{OUTPUT_DIR}')")

    # Summary
    print_section("Summary")

    print(f"""
What we did:
1. Loaded GPT-2 (124M parameters)
2. Added LoRA adapter ({trainable_params:,} trainable params = {100 * trainable_params / total_params:.2f}%)
3. Continued pre-training on medical domain text
4. Model now better understands medical terminology

Key Takeaways:
- LoRA allows efficient adaptation with <1% of parameters
- Domain adaptation improves domain-specific generation
- This works on CPU with small models
- For production: use larger models + GPUs + more data

Next Steps:
1. Try with your own domain data (see EXERCISES.md)
2. Experiment with different LoRA configurations
3. Compare before/after predictions more carefully
4. Try larger models if you have a GPU
""")

    print_section("Demo Complete!")


if __name__ == "__main__":
    main()
