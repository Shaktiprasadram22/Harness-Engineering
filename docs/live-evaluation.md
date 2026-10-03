# Live local-model evaluation

A real Qwen3 0.6B Q8_0 model was run locally through Ollama 0.35.1 on CPU. The scripted provider was not used in this experiment. This small synthetic inventory task measures a narrow harness, not general agent intelligence.

## Experiment

The frozen before harness already required explicit branches. It is separate from the deliberately Central-default baseline in the offline experiment. Sixteen development scenarios include twelve single-turn checks and four conversations. Six additional transfer scenarios were reserved until the candidate source was frozen. Dataset hashes and the plan were committed before real-model inference.

Each scenario runs three times with seeds 42–44, temperature 0, thinking disabled, a 256-token generation cap, a 4096-token context, and four CPU threads. These repeated greedy runs are consistency checks, not independent statistical samples. Every scenario starts with a fresh agent; its conversation turns share history. Primary success requires every expected turn to pass, with actual tool evidence for factual answers.

The same author knows both datasets. “Reserved” means not used as evaluation feedback while tuning, not a blind external benchmark. No expected answers are included in model input. The final public datasets are future development material, not permanently unseen tests.

## Development results

| Metric | Before | Candidate |
| :--- | ---: | ---: |
| Whole-scenario passes | 18/48 (37.5%) | 30/48 (62.5%) |
| Individual-turn passes | 21/60 (35%) | 42/60 (70%) |
| Multi-turn scenario passes | 0/12 | 0/12 |

No development case regressed in its scenario pass count. The candidate improved ordinary plural stock requests and one missing-branch case. It did **not** solve live conversation routing: the model returned unsupported prose on follow-up turns, causing safe abstention. On some single-turn quantity requests it called `list_products` instead, and the harness returns the first successful tool result. Aggregate-stock and the missing-branch blue-notebook cases also remained failures. A deterministic unit test of the branch resolver is not evidence that the live model routes a conversation successfully.

This is a measured partial improvement, not a claim that the agent now passes all conversations. The remaining routing failures are preserved in the reports and were not hidden or tuned away using transfer results.

## Reserved transfer results

| Metric | Before | Candidate |
| :--- | ---: | ---: |
| Whole-scenario passes | 3/18 | 9/18 |
| Individual-turn passes | 3/27 | 18/27 |

The candidate was frozen before these runs and was not retuned from transfer output. Ordinary quantity, zero-stock, and clarification cases passed; all three reserved conversation scenarios failed. This supports a narrow improvement in the tested single-turn interface, not successful general conversation handling.

## Recorded resource use

| Run | Median model-call milliseconds | Prompt tokens | Generated tokens |
| :--- | ---: | ---: | ---: |
| before-development | 914.72 | 23745 | 1201 |
| after-development | 1008.383 | 28809 | 1284 |
| before-transfer | 1122.311 | 10887 | 576 |
| after-transfer | 1193.722 | 13131 | 618 |

The candidate uses a longer system prompt. Improved outcomes came with more prompt tokens; latency was not improved in this run. See order and warm-up limitations below.

## What the traces revealed

The original harness failed ordinary plural product requests because the model sent `blue notebooks` but the inventory stores `blue notebook`. Missing-branch questions sometimes received unsupported model text and were safely abstained from rather than correctly clarified. The strict current-message branch rule could not resolve “same branch” or “other branch.”

The candidate advertises catalog names and the tool clarification path, canonicalizes only exact names or simple trailing-s plurals, and resolves supported references from the last tool-verified single branch. Explicit mismatches remain denied; missing branches remain missing without a supported reference. An all-branches result clears the single-branch anchor. Session version 2 preserves the anchor, validates its value, and accepts old version 1 sessions without an anchor.

These changes are bounded interface/context fixes. They do not make the model choose the correct tool for every request, support unrestricted English references, or provide an OS sandbox.

## Reproduce

Install Ollama and import the official [Qwen GGUF artifact](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/tree/23749fefcc72300e3a2ad315e1317431b06b590a).

```text
File: Qwen3-0.6B-Q8_0.gguf
Bytes: 639446688
SHA256: 9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031
```

After verifying the artifact, create a Modelfile with `FROM /absolute/path/Qwen3-0.6B-Q8_0.gguf`, then:

```sh
ollama create qwen3-eval:0.6b-q8 -f Modelfile
python -m evals.live --variant before --model qwen3-eval:0.6b-q8 \
  --dataset evals/live-development.json --output artifacts/before-dev.json
python -m evals.live --variant after --model qwen3-eval:0.6b-q8 \
  --dataset evals/live-development.json --output artifacts/after-dev.json
python -m evals.live --variant before --model qwen3-eval:0.6b-q8 \
  --dataset evals/live-transfer.json --output artifacts/before-transfer.json
python -m evals.live --variant after --model qwen3-eval:0.6b-q8 \
  --dataset evals/live-transfer.json --output artifacts/after-transfer.json
```

The recorded server used `http://127.0.0.1:11439`; pass `--endpoint` for that setup. Default endpoint is port 11434. Model weights and the runtime are external assets, not committed to this repository.

## Reading the evidence

Inspect [before development](results/live-before-development.json), [after development](results/live-after-development.json), [before transfer](results/live-before-transfer.json), and [after transfer](results/live-after-transfer.json). The [pre-inference dataset freeze](../evals/live-freeze.json) and [candidate source freeze](../evals/live-candidate-freeze.json) record their timing and hashes.

Full reports preserve model inputs/responses, tool results, expectations, per-turn and per-scenario grades, tokens, latency, model digest, source/data/dataset hashes, and Git state. A data-result “ok” is not necessarily a scenario pass: a product list is valid tool output but fails a quantity question.

Measured call latency includes provider round trips and may include model loading; before/after order and warm caches can affect comparisons. Local inference has no API bill, but uses compute, memory, electricity, and time. These tiny synthetic datasets do not establish production reliability or broad safety.
