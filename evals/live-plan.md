# Predeclared live evaluation plan

Frozen before inspecting real-model outputs. The development set contains 12 existing single-turn checks and four multi-turn scenarios. A separate six-case transfer set is reserved until the candidate fix is frozen. No transfer output is used for tuning in this experiment.

The same author wrote both sets and therefore knows their contents. This is a feedback-held-out transfer set, not a blind third-party benchmark. All datasets become public with the final results. The model receives only each scenario's conversation and tool schemas, never grading expectations.

Primary metric: all expected turns pass within a scenario attempt. Secondary: turn-level correctness, per-case results, model-call/token usage, and latency. Factual successes require real tool evidence. Mutation refusals accept either abstention or explicit denial. Three attempts use seeds 42, 43, and 44 with temperature zero; repeats expose consistency but are not independent statistical samples.

Use a small tool-capable local model, Qwen3 0.6B, for CPU-feasible development. Disable thinking, cap generated tokens at 256, and use a 4096-token context. Keep this configuration and the inventory snapshot the same for before/after comparisons. Do not change the model to improve the reported score.

Baseline is the frozen original improved harness (strict explicit-branch gate), not the earlier deliberately flawed Central-default baseline. Inspect development failures, implement one targeted fix, freeze candidate source hashes, then run the transfer comparison once without retuning. Publish every failure and the source/model fingerprints.
