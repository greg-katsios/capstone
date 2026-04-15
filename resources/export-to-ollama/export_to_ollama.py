#!/usr/bin/env python3
"""
Export a LoRA-adapted model to Ollama.

Takes the adapter saved by adapt_model.py (or any PEFT LoRA adapter),
merges it back into the base model, and registers it in Ollama so you
can use it in your Streamlit persona apps.

Usage:
    # Basic — merge and register with defaults
    python export_to_ollama.py

    # Custom name + quantization
    python export_to_ollama.py --model-name medical-persona --quantize q4_K_M

    # With a system prompt baked in
    python export_to_ollama.py --model-name medical-persona \
        --system-prompt "You are a medical expert who explains conditions in plain language."

    # Point to a different adapter directory
    python export_to_ollama.py --adapter-dir ./my_custom_adapter
"""

import argparse
import os
import shutil
import subprocess
import sys
import textwrap

import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoTokenizer


# ── Formatting helpers (same style as adapt_model.py) ────────────

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_step(n, title):
    """Print a numbered step header."""
    print(f"\n── Step {n}: {title} " + "─" * max(0, 43 - len(title)))


# ── Core pipeline ────────────────────────────────────────────────

def merge_adapter(adapter_dir, merged_dir):
    """
    Load a LoRA adapter and merge it into the base model.

    After LoRA training, your adapter weights are stored separately
    from the base model.  Ollama needs a single, complete model,
    so we merge them together with merge_and_unload().
    """
    print_step(1, "Merge LoRA adapter into base model")

    if not os.path.isdir(adapter_dir):
        print(f"ERROR: Adapter directory not found: {adapter_dir}")
        print("Make sure you've run adapt_model.py first.")
        sys.exit(1)

    print(f"Loading adapter from: {adapter_dir}")

    # AutoPeftModelForCausalLM knows how to load a PEFT adapter
    # and the base model it was trained on (recorded in adapter_config.json).
    model = AutoPeftModelForCausalLM.from_pretrained(
        adapter_dir,
        torch_dtype=torch.float16,
        device_map="cpu",
    )
    tokenizer = AutoTokenizer.from_pretrained(adapter_dir)

    print("Merging LoRA weights into base model...")

    # merge_and_unload() folds the low-rank matrices back into the
    # original weight matrices, producing a normal model with no
    # adapter overhead.  This is irreversible — keep your adapter
    # directory if you want to experiment later.
    merged_model = model.merge_and_unload()

    # Save the merged model in HuggingFace safetensors format.
    # Ollama can read this directly — no GGUF conversion needed.
    if os.path.isdir(merged_dir):
        shutil.rmtree(merged_dir)

    merged_model.save_pretrained(merged_dir)
    tokenizer.save_pretrained(merged_dir)

    param_count = sum(p.numel() for p in merged_model.parameters())
    size_gb = sum(
        p.numel() * p.element_size() for p in merged_model.parameters()
    ) / (1024 ** 3)

    print(f"\n[OK] Merged model saved to: {merged_dir}")
    print(f"     Parameters: {param_count:,}")
    print(f"     Size on disk: ~{size_gb:.1f} GB (fp16)")

    return merged_dir


def write_modelfile(merged_dir, modelfile_path, system_prompt=None):
    """
    Write an Ollama Modelfile.

    A Modelfile is to Ollama what a Dockerfile is to Docker — it
    describes how to build a model.  At minimum it needs a FROM line
    pointing to your model weights.
    """
    print_step(2, "Write Modelfile")

    # Use absolute path so Ollama can find the model from any cwd.
    abs_model_dir = os.path.abspath(merged_dir)

    lines = []

    # FROM points to the merged safetensors directory.
    # Ollama reads the config.json + *.safetensors files directly.
    lines.append(f"FROM {abs_model_dir}")
    lines.append("")

    # Sensible defaults for conversational personas.
    lines.append("# Generation parameters")
    lines.append("PARAMETER temperature 0.7")
    lines.append("PARAMETER top_p 0.9")
    lines.append("PARAMETER num_ctx 2048")
    lines.append("")

    if system_prompt:
        # Triple-quote syntax for multi-line system prompts.
        lines.append('SYSTEM """')
        lines.append(system_prompt)
        lines.append('"""')
        lines.append("")

    content = "\n".join(lines)

    with open(modelfile_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] Modelfile written to: {modelfile_path}")
    print()
    print("     Contents:")
    for line in content.strip().splitlines():
        print(f"       {line}")

    return modelfile_path


def register_in_ollama(model_name, modelfile_path, quantize=None):
    """
    Run 'ollama create' to register the model.

    This tells Ollama to read the Modelfile, import the weights, and
    make the model available for 'ollama run' and the Python API.
    """
    print_step(3, "Register in Ollama")

    # Check that Ollama is installed.
    if not shutil.which("ollama"):
        print("ERROR: 'ollama' command not found.")
        print("Install Ollama from https://ollama.com/download")
        sys.exit(1)

    cmd = ["ollama", "create", model_name, "-f", modelfile_path]

    if quantize:
        # --quantize tells Ollama to quantize during import.
        # Options: q8_0 (best quality), q4_K_M (balanced), q4_K_S (smallest).
        cmd.extend(["--quantize", quantize])
        print(f"Registering '{model_name}' with {quantize} quantization...")
        print("(This may take a few minutes for larger models.)")
    else:
        print(f"Registering '{model_name}' (no quantization — full precision)...")

    print(f"Running: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print(f"\nERROR: 'ollama create' failed (exit code {result.returncode}).")
        print("Common fixes:")
        print("  - Make sure the Ollama app/service is running")
        print("  - Check that the merged model directory exists")
        print("  - Try a smaller quantization (q4_K_M) if you're low on RAM")
        sys.exit(1)

    print(f"\n[OK] Model '{model_name}' registered in Ollama!")


def verify_model(model_name):
    """
    Verify the model is registered and run a quick test.
    """
    print_step(4, "Verify and test")

    # Check ollama list
    print("Checking 'ollama list'...\n")
    subprocess.run(["ollama", "list"])

    # Try a quick generation via the Ollama Python API
    print(f"\nTesting '{model_name}' with a quick prompt...\n")
    try:
        from ollama import chat

        response = chat(
            model=model_name,
            messages=[{"role": "user", "content": "Hello! Tell me about yourself in one sentence."}],
        )
        reply = response["message"]["content"]
        print(f"  Prompt:   'Hello! Tell me about yourself in one sentence.'")
        print(f"  Response: {reply}")
        print(f"\n[OK] Model is working!")
    except ImportError:
        print("  (Ollama Python package not installed — skipping API test.)")
        print(f"  You can test manually: ollama run {model_name}")
    except Exception as e:
        print(f"  API test failed: {e}")
        print(f"  Try manually: ollama run {model_name}")


# ── Main ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Export a LoRA-adapted model to Ollama.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python export_to_ollama.py
              python export_to_ollama.py --model-name medical-persona --quantize q4_K_M
              python export_to_ollama.py --system-prompt "You are a helpful medical expert."
        """),
    )
    parser.add_argument(
        "--adapter-dir",
        default="./adapted_model",
        help="Path to the saved LoRA adapter (default: ./adapted_model)",
    )
    parser.add_argument(
        "--model-name",
        default="my-persona",
        help="Name to register in Ollama (default: my-persona)",
    )
    parser.add_argument(
        "--system-prompt",
        default=None,
        help="System prompt to bake into the Modelfile (optional)",
    )
    parser.add_argument(
        "--quantize",
        choices=["q8_0", "q4_K_M", "q4_K_S"],
        default=None,
        help="Quantize during import: q8_0 (best), q4_K_M (balanced), q4_K_S (smallest)",
    )
    parser.add_argument(
        "--merged-dir",
        default="./merged_model",
        help="Where to save the merged model (default: ./merged_model)",
    )

    args = parser.parse_args()

    print_section("Export to Ollama")
    print(f"""
    Adapter directory:  {args.adapter_dir}
    Merged output:      {args.merged_dir}
    Ollama model name:  {args.model_name}
    Quantization:       {args.quantize or 'none (full precision)'}
    System prompt:      {'yes' if args.system_prompt else 'none'}
    """)

    # Step 1: Merge LoRA adapter into the base model
    merged_dir = merge_adapter(args.adapter_dir, args.merged_dir)

    # Step 2: Write a Modelfile for Ollama
    modelfile_path = os.path.join(merged_dir, "Modelfile")
    write_modelfile(merged_dir, modelfile_path, args.system_prompt)

    # Step 3: Register the model in Ollama
    register_in_ollama(args.model_name, modelfile_path, args.quantize)

    # Step 4: Verify and test
    verify_model(args.model_name)

    # Summary
    print_section("Done!")
    print(f"""
    Your fine-tuned model is now available in Ollama.

    Quick reference:
      ollama run {args.model_name}          # Interactive chat
      ollama list                           # Verify registration
      ollama rm {args.model_name}           # Remove if needed

    To use in your Streamlit persona app, set the model name to:
      model: "{args.model_name}"

    Files created:
      {os.path.abspath(args.merged_dir)}/     # Merged model weights
      {os.path.abspath(modelfile_path)}       # Ollama Modelfile
    """)


if __name__ == "__main__":
    main()
