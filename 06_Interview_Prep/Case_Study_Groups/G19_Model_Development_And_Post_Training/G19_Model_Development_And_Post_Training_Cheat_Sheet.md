# G19 — Model Development and Post-Training: Cheat Sheet

[Main](G19_Model_Development_And_Post_Training_Main.md) · [Deep Dive](G19_Model_Development_And_Post_Training_Deep_Dive.md) · [Unchanged source](G19_Model_Development_And_Post_Training.md)

## Ask first

Math level? Final answer or valid working? Tools allowed? Who uses it? Base-model adaptation or pretraining? GPU/device budget?

## Whiteboard path

`Checkable data → dedupe/decontaminate → SFT format → sample model attempts → verifier/step/preference score → controlled update → held-out eval gate → optional distill/quantize → serve → reviewed data feedback`

The model is trained; deterministic checks and human labels control advancement.

## Numbers are source assumptions

Training ≈ `6ND` FLOPs; generation ≈ `2N` FLOPs/token. 7B × 50M SFT tokens ≈ 2.1e18 FLOPs. 400M rollout tokens ≈ 5.6e18 to generate plus 1.68e19 to update. Full Adam state ~16 bytes/parameter, or ~112GB for 7B before activations.

## Gate and pivots

- SFT teaches format; verified rollouts optimize correctness. Step grading is needed when working itself matters.
- Decontaminate and split by source/time; report pass@1 and sampling settings.
- Gate math, general regression, ill-posed answers, harmful compliance **and** over-refusal.
- Compute pivot: small ablations, adapters, targeted rollouts, full-state checkpoints, eval gain/GPU-hour.
- Phone pivot: student model, 4-bit weights plus KV/runtime, and on-device politeness/latency/battery checks.

**60-second close:** “Pin the target, use verified data, keep SFT short, score the model’s own attempts with the right checker, and promote only checkpoints that pass a clean multi-dimensional gate.”
