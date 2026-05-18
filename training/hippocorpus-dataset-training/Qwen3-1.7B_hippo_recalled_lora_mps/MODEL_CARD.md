# Qwen3-1.7B HippoCorpus LoRA Adapter

## Model Details

### Model Description

This is a LoRA (Low-Rank Adaptation) adapter fine-tuned on the [Qwen3-1.7B](https://huggingface.co/Qwen/Qwen3-1.7B) language model, specialized for generating autobiographical narratives and personal memories in the style of the HippoCorpus dataset. The adapter enables the base model to produce more natural and contextually appropriate responses when discussing personal experiences, memories, and autobiographical content.

- **Model Type:** Causal Language Model (with LoRA adaptation)
- **Base Model:** Qwen/Qwen3-1.7B
- **Fine-tuning Method:** LoRA (Low-Rank Adaptation)
- **Framework:** Transformers, PEFT (Parameter-Efficient Fine-Tuning)
- **Language:** English

### Model Specifications

- **Total Parameters (Base Model):** 1.7B
- **LoRA Configuration:**
  - Rank (r): 8
  - Alpha (lora_alpha): 16
  - Dropout: 0.05
  - Target Modules: q_proj, v_proj (query and value projections in attention layers)
  - Bias: none
  - Task Type: Causal Language Modeling
- **Maximum Context Length:** 256 tokens
- **Trainable Parameters:** ~25,000 (less than 0.002% of base model)

## Training Details

### Dataset

**HippoCorpus: A Large-Scale Personal Memory Dataset**

- **Source:** Allen Institute for AI - [HippoCorpus Dataset](https://allenai.org/hippocorpus)
- **Subset Used:** Recalled memories only (autobiographical personal memories from real users)
- **Total Stories in Full Dataset:** 6,854 stories across three categories (recalled, imagined, retold)
- **Stories in Training Set:** ~6,200 recalled memories (after filtering)
- **Data Characteristics:**
  - Personal diary-like narratives
  - First-person accounts of memories and experiences
  - Diverse topics: relationships, travel, learning experiences, challenges overcome, celebrations, etc.
  - Average story length: 200-300 words
  - Natural, conversational language patterns

### Training Configuration

- **Number of Epochs:** 2
- **Learning Rate:** 2e-4 (cosine decay scheduler)
- **Warmup Steps:** 10
- **Per-Device Batch Size:** 1
- **Gradient Accumulation Steps:** 8
- **Effective Batch Size:** 8
- **Total Training Steps:** ~1,550 (approximately)
- **Evaluation Strategy:** None (no validation evaluation during training)
- **Save Strategy:** Checkpoint saved after each epoch
- **Device Optimization:** CPU/MPS/DirectML/CUDA compatible

### Data Preprocessing

- Text normalization: Removal of extra whitespace and standardization
- Tokenization: Fast tokenizer from HuggingFace Transformers
- Padding: No padding applied during preprocessing (handled by data collator)
- Truncation: Applied at 256 tokens maximum length

### Training Framework

- **Library:** Hugging Face Transformers + PEFT
- **Trainer:** Custom DebugTrainer (extended HuggingFace Trainer with debugging capabilities)
- **Optimizer:** AdamW (default in TrainingArguments)
- **Loss Function:** Cross-entropy language modeling loss
- **Gradient Checkpointing:** Enabled for memory efficiency

## Intended Use

### Primary Use Cases

1. **Autobiographical Content Generation:** Generate realistic personal narratives and memory-like text
2. **AI Persona Development:** Foundation for persona systems that need to narrate personal experiences naturally
3. **Memory-Based Storytelling:** Systems that generate first-person accounts of experiences
4. **Conversational Agents:** Personas that discuss personal background, memories, and life experiences authentically
5. **Educational Applications:** Training data for understanding autobiographical narrative patterns

### Out of Scope

- General-purpose text generation (consider base Qwen model instead)
- Technical or domain-specialized content generation
- Real-time translation or multilingual tasks
- Critical decision-making systems

## How to Use

### Loading the Model

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load base model
base_model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-1.7B")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-1.7B")

# Load LoRA adapter
model = PeftModel.from_pretrained(
    base_model,
    "path/to/Qwen3-1.7B_hippo_recalled_lora_mps"
)
```

### Inference Example

```python
# Prepare input
prompt = "I remember the time when I first learned to"

# Tokenize
inputs = tokenizer(prompt, return_tensors="pt")

# Generate
output_ids = model.generate(
    inputs["input_ids"],
    max_length=256,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)

# Decode
generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print(generated_text)
```

### With Streamlit Integration

This model is designed for integration with the INF191 Capstone AI Personas platform:

```python
from transformers import pipeline

# Create text generation pipeline
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0  # GPU device or -1 for CPU
)

# Generate memory-like text
result = generator(
    "One summer, I decided to",
    max_length=200,
    num_return_sequences=1,
    temperature=0.8
)
```

## Model Performance and Limitations

### Performance Characteristics

- **Training Time:** ~2-3 hours on consumer GPU (MPS/CUDA/DirectML)
- **Model Size (LoRA Adapter):** ~100 KB (adapter_model.safetensors)
- **Full Model Size (with base):** ~3.5 GB (1.7B base + adapter weights)
- **Inference Speed:** ~50-200 tokens/second depending on hardware

### Known Limitations

1. **Domain-Specific:** Optimized for autobiographical narratives; may not perform well on technical or specialized content
2. **Context Length:** Limited to 256 tokens for training; longer sequences may not be handled as effectively
3. **Factuality:** Generated content is not factually grounded; narratives are synthetic autobiography
4. **Bias:** May inherit biases from the HippoCorpus dataset (primarily English-speaking, internet-using population)
5. **Creativity vs. Authenticity:** Balances between realistic memory-like text and creative generation

### Recommendations for Use

- **Prompt Engineering:** Experiment with different prompts starting with memory triggers ("I remember...", "One day I...", "When I was...")
- **Temperature Settings:** Use 0.7-0.9 for narrative generation; lower values for more factual/consistent output
- **Sampling:** Use top-k or top-p sampling for more diverse generations
- **Length Control:** Set max_length between 100-250 tokens for best quality narratives
- **Post-processing:** Consider filtering or ranking multiple generated candidates for coherence and naturalness

## Technical Specifications

### Dependencies

- `transformers >= 4.30.0`
- `peft >= 0.4.0`
- `torch >= 2.0.0`
- `datasets >= 2.10.0`
- `pandas >= 1.3.0`

### Hardware Requirements

- **Minimum:** 4GB VRAM (for inference with quantization or CPU)
- **Recommended:** 8GB VRAM for smooth inference
- **Training:** 8GB+ VRAM or CPU-compatible device (MPS/DirectML)

### Supported Devices

- NVIDIA CUDA GPUs
- Apple Metal Performance Shaders (MPS)
- AMD GPUs (via DirectML on Windows or ROCm on Linux)
- CPU (with reduced performance)

## Training Dataset Attribution

**HippoCorpus Dataset:**

- **Citation:** Sap et al., 2020. "Social IQa: Commonsense reasoning about social interactions." EMNLP 2019
- **Dataset Homepage:** [HippoCorpus on AllenAI](https://allenai.org/hippocorpus)
- **Paper:** [Memory narratives on the social web](https://arxiv.org/abs/1811.00945)
- **License:** Research use; see original dataset for details

## Capstone Project Context

This model was developed as part of the **INF191 Capstone Project: Persona Weave** at the University of California. The project explores:

- Domain-adaptive training for persona development
- Autobiographical narrative generation
- Integration with the Model Context Protocol (MCP)
- Evaluation of emotionally-intelligent conversational systems

### Project Components Using This Model

1. **Persona System:** Enables AI personas to generate and discuss personal memories and backgrounds
2. **Conversation History:** Integrated with conversational memory systems for context-aware responses
3. **Evaluation Framework:** Metrics include perplexity, generation rubric scores, and lexical diversity
4. **Platform:** Streamlit-based agentic interface for multi-persona interactions

## Evaluation

### Training Metrics

- **Final Training Loss:** Monitored via HuggingFace Trainer
- **Checkpoints:** Saved after epoch 1 and epoch 2
- **Validation:** Not conducted during training (eval_strategy='no')

### Recommended External Evaluations

To assess the quality of generations, consider:

1. **Perplexity:** On HippoCorpus test set or out-of-domain narratives
2. **BLEU/ROUGE:** Against reference autobiographical texts
3. **Human Evaluation:** 
   - Naturalness of generated narratives
   - Authenticity (how "memory-like" the text sounds)
   - Coherence and narrative flow
   - Emotional appropriateness
4. **Lexical Diversity:** Vocabulary richness compared to base model

## Versioning and Checkpoints

- **Adapter Version:** 1.0
- **Base Model Commit:** Qwen/Qwen3-1.7B (latest from HuggingFace)
- **PEFT Version:** 0.19.1
- **Available Checkpoints:**
  - `checkpoint-348/`: After epoch 1
  - `checkpoint-696/`: After epoch 2 (final)

## License and Usage Rights

This LoRA adapter is provided for research and educational purposes as part of the INF191 Capstone Project. The base Qwen3-1.7B model is governed by the Qwen License Agreement. Please refer to:

- **Base Model License:** [Qwen Model License](https://huggingface.co/Qwen/Qwen3-1.7B)
- **Dataset License:** HippoCorpus dataset terms

## Contact and Attribution

- **Developed By:** INF191 Capstone Team
- **Project Partner:** Leidos
- **Institution:** University of California
- **Base Model:** Alibaba's Qwen Team
- **Training Framework:** Hugging Face & Meta AI (PEFT)

## Acknowledgments

- Allen Institute for AI for the HippoCorpus dataset
- Alibaba Qwen team for the base model
- Hugging Face for the Transformers and PEFT libraries
- Course instructor and project advisors

---

**Model Card Last Updated:** May 2026  
**Compatible With:** Transformers v4.30+, PEFT v0.4+

