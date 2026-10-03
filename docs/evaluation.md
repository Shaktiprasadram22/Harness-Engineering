# Evaluation · explicit branch selection

## Problem and intervention

The baseline silently defaults to Central when branch is omitted. In a two-branch inventory, “How many blue notebooks?” is ambiguous. The improved policy requires an explicit branch and asks for clarification instead of guessing.

The harness additionally removes a model-guessed branch if the current question does not explicitly select one. The unit suite checks this even with an intentionally misbehaving provider.

## Measured offline results

12 public development cases × 3 repeats per policy:

| Group | Baseline | Improved |
| :--- | ---: | ---: |
| Known weakness: missing branch | 0/9 | 9/9 |
| Regression guards | 27/27 | 27/27 |
| **Total** | **27/36 (75%)** | **36/36 (100%)** |

**These are deterministic harness results, not model accuracy.** Repeating a scripted provider does not measure LLM reliability. Repeats demonstrate the reporting format and execution consistency; use the live provider to study model variation.

All case specifications are public, including expected values. None are held-out. Assertions check structured outcomes and evidence, not whether an expected number happened to appear in prose. Reorder membership and product lists are checked exactly.

The reference expectations were manually checked against the committed synthetic CSV. If the fixture changes, update and independently review those expectations.

## Evidence and reproduction

[Full recorded results](results/offline-evaluation.json) contain every attempt, tool arguments, results, timing, item-level at-least-once/all-attempt outcomes, dataset and data hashes, and source hashes. The report records the base Git commit and whether the working tree was dirty; source fingerprints identify the actual implementation evaluated before the implementation commit.

```sh
python -m unittest discover -s tests -v
python -m evals.run --repeats 3 --output artifacts/evaluation.json
```

At-least-once and all-attempt fields refer to the `k` repeated runs actually recorded. They are empirical task summaries, not probability estimates or guarantees.

## What this establishes

The measured change fixes three missing-branch cases while preserving nine existing behaviors: exact stock, aggregation, zero stock, unknown products, product listing, reorder reporting, and unsupported mutation/secret requests.

The tests also check unknown tool denial, argument validation, unsupported model claims, bounded retries, session persistence, malformed messages, and the Ollama HTTP contract with a mocked server.

## What remains unverified

This offline experiment does not measure a live model or transfer behavior. A separate [live local-model experiment](live-evaluation.md) now records model calls, tokens, latency, conversation cases, and reserved transfer checks. There is still no concurrency/load evaluation, arbitrary-language support, or OS sandbox. Both suites are small and do not establish comprehensive security. Offline timings below remain Python harness timings, not model inference timings.

The [current offline rerun](results/offline-evaluation-current.json) preserves the same 27/36 baseline and 36/36 improved result after the live-development harness changes. The original report is retained with its original source fingerprints.
