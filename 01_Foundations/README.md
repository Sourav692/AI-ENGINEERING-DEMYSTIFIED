# 01 — Foundations

**Prerequisites: none.** Nothing in this group depends on a framework. Start here if you're new; skip if you already write Python comfortably and have used a model API directly.

**2 phases · 61 notebooks**

## Topics covered

### `00_Theory_and_Foundations/` — 51 notebooks

**`Model_Landscape_and_Hugging_Face/`** — 21 notebooks
- The Hugging Face Hub
- Transformers
- Diffusers
- Audio and video models
- Building demos with Gradio

**`Fine_Tuning_and_RL/`**
- Supervised fine-tuning end to end
- Data preparation
- Training
- Evaluation
- Llama 2 with AutoTrain
- 🚧 RLHF, DPO and LoRA — planned, not built

**`Coding_Essentials_for_Agents/`** — the Python an agent engineer actually needs
- Python fundamentals
- Files and databases
- Flask APIs
- Calling LLM APIs raw
- Threading and the GIL
- Asyncio

**`Math_and_ML_Intuition/`** · **`Transformer_Architecture/`**
- 🚧 Planned — scope READMEs only

### `02_Prompt_and_Context_Engineering/` — 10 notebooks

**`Prompt_Engineering/`**
- Core prompting patterns
- Advanced prompting patterns
- Hands-on comparisons across models
- Multimodal prompting
- Real-world applications

**`Context_Engineering/`**
- 🚧 Planned

## How to work through it

Coding essentials → Hugging Face → prompting. Fine-tuning is optional at this stage and can wait until after `02_Core/`.

Requires the `hf` extra for the Hugging Face material: `uv pip install -e ".[hf]"` (large download — torch, transformers, diffusers).

## What is deliberately *not* here

Framework mechanics. LangChain's prompt templates are LangChain, not prompting — they live in `02_Core/01_LangChain_Fundamentals/`.
