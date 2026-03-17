import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    dtype=torch.float32,
).to("mps")

inputs = tokenizer("Hello world", return_tensors="pt")
inputs = {k: v.to("mps") for k, v in inputs.items()}

with torch.no_grad():
    out = model(**inputs)

print("Success! Output shape:", out.logits.shape)