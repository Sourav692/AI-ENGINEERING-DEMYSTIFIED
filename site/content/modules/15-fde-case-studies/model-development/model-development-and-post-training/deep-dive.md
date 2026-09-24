# G19 — Model Development and Post-Training: Deep Dive

> Read with the unchanged [source](/modules/15-fde-case-studies/model-development/model-development-and-post-training#full-pack). The [Main guide](/modules/15-fde-case-studies/model-development/model-development-and-post-training#main) is the interview path; the [Cheat Sheet](/modules/15-fde-case-studies/model-development/model-development-and-post-training#cheat-sheet) is the recall card. Most design choices in the source are constructed from prompts and general practice, so distinguish assumptions from measured results.

## 1. Data quality and split integrity

Math's advantage is program-checkable final answers. Use public, licensed, expert-written and filtered synthetic problems. Rejection sampling keeps synthetic answers only when verified. Deduplicate near-duplicates before train/test splitting, then separate by time and source; random splits over near-identical traces inflate accuracy. Record a datasheet with collection period, filters, split method, label source and known bias. Use human adjudication for hard, high-impact or low-agreement labels. A source example of duplicated traces produced a 94% offline score but roughly 78% production performance; after deduplication/time split/relabeling, the honest offline score was near 83%.

## 2. SFT, scoring and updates

SFT pairs prompts with worked solutions and marked final answers. It teaches instruction following and format; training too long on narrow data can memorize phrasing or erode general behavior. Include general instruction examples and legitimate “no unique answer” cases. Parameter-efficient adapters speed recipe search; QLoRA lowers base-weight memory further. A full update is justified only when the adapter misses a measured target.

For post-training, sample multiple candidate answers per problem. A program verifier is efficient for final-answer correctness but misses invalid working. A step reward or human review addresses reasoning quality. Preference pairs work for tone, clarity and refusal boundaries, but graders may favor verbosity. RL with a verifier benefits from a reference-model drift penalty; DPO gives a simpler preference-pair path. Audit high-scoring samples every round to detect reward hacking.

## 3. Arithmetic and compute-constrained variant

Rules of thumb: training FLOPs ≈ `6 × parameters × tokens`; generation FLOPs ≈ `2 × parameters × generated tokens`. The source's assumed 7B/50M-token SFT is ~2.1e18 FLOPs. Its 400M rollout tokens are ~5.6e18 generation FLOPs and ~1.68e19 update FLOPs. Full Adam fine-tuning at roughly 16 bytes/parameter puts 7B weights/gradients/optimizer state near 112GB before activations, beyond one 80GB card.

In #73's pretraining variant, an illustrative 20 tokens/parameter means 140B tokens for 7B and ~5.88e21 FLOPs. At assumed 3e14 effective FLOP/s per GPU, that is ~5,444 GPU-hours; these are whiteboard estimates. Fit the memory first: data parallel if a model fits; ZeRO/FSDP when optimizer state does not; tensor parallel when layers do not; pipeline parallel when depth needs splitting; recomputation and mixed precision for activations. Stream quality-filtered shards, record shard order and checkpoint optimizer plus data-loader position. Track model FLOPs utilization and eval gain/GPU-hour, not only GPUs allocated.

## 4. Evaluation and alternate objectives

Gate on pass@1 for clean unseen problems, valid working on a stratified sample, general regression, fabrication on ill-posed problems and safety/over-refusal. Report temperature and sampling method: greedy pass@1 cannot be compared to majority vote over eight samples. Check overlap by n-grams/embeddings and attach a contamination report. Treat an unexpectedly large gain as a leakage investigation, not an automatic win.

For #81, plot harmful-compliance rate against over-refusal on benign prompts that sound risky. A model that refuses everything fails usefulness. Define written policy; use preference pairs for helpful and safe behavior, AI feedback only with human auditing, and red-team cases in the gate. An input/output safety classifier can change faster than weights. For #83, distill a teacher into a 1B–3B student, quantize to fit device memory and evaluate polite behavior with rude or provocative prompts. Include KV cache, runtime overhead, first-token time, tokens/s and battery on-device; a full-precision server eval is insufficient.

## 5. When weights are the right surface

Try context, memory and procedure before parameter updates when the issue is missing knowledge or workflow design. Weights earn their cost for high-volume strict behavior/format, missing domain vocabulary or a hard latency/cost ceiling after cheaper surfaces are exhausted. Fine-tuning freezes a task definition and is slower to revise when requirements change; keep a prompted fallback where useful. A compute spike should prompt small-model ablations, adapters, targeted rollouts and frequent checkpoints before another full-scale run.
