<!-- Loaded by Claude Code in addition to the root CLAUDE.md when working under this folder. Root rules still apply; this file adds what is specific to this phase. -->

# Phase 00 — Theory & Foundations

**Owns:** everything with no framework prerequisite — Python, the Hugging Face ecosystem, fine-tuning, and the maths/architecture background. Stage `01_Foundations/`.

| Track | State | Content |
|---|---|---|
| `Model_Landscape_and_Hugging_Face/` | Built | HF Hub setup, Transformers, Diffusers, audio/video models, Gradio (21 notebooks) |
| `Fine_Tuning_and_RL/` | Built | SFT, data prep, training, eval (DeepLearning.AI labs) + Llama 2 AutoTrain. `02_Techniques/` (RLHF/DPO/LoRA) is planned |
| `Coding_Essentials_for_Agents/` | Built | Python, files/DBs, Flask APIs, raw LLM API calls, threading/GIL, asyncio |
| `Math_and_ML_Intuition/`, `Transformer_Architecture/` | Planned | scope READMEs only — no content |

## Conventions here

- **Do not use the `helpers` factory in this phase.** Zero notebooks import it, deliberately: this is where raw provider SDKs and HF pipelines are taught, so clients are constructed explicitly. Introducing `get_llm()` here would hide the thing being taught.
- Needs the `hf` extra (`uv pip install -e ".[hf]"`) — transformers/torch/diffusers/peft/trl, a large download. Don't add it to the core spine.
- 51 notebooks, the second-largest phase by content.

## Don't

- Don't put prompting content here — it belongs to `01_Foundations/02_Prompt_and_Context_Engineering/`.
- Don't add agent-building material; that's `02_Core/05_AI_Agent_Fundamentals/`.
