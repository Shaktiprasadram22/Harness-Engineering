# Chapter coverage review

The first version of these notes was selective. This review expands all eleven chapters with mechanisms, distinctions, failure examples, and short definitions. It does **not** certify that every spoken point in all eleven videos is covered.

**Source boundary:** Chapters 1–10 were compared with the creator’s linked companion articles. Chapter 11 remains based on its published description and repository links; its complete transcript was unavailable. Examples added to teach the concepts are original and are not additional claims about the creator’s measured results.

## What was added

| Chapter | Gap in the earlier explanation | Added reading |
| :--- | :--- | :--- |
| [1 · System](../chapters/01-the-system-around-the-model.md#diagnose-the-layer-before-changing-the-model) | Layer diagnosis and the difference between instructions, enforcement, and evidence | Travel-booking failure table; manager calls versus handoffs |
| [2 · Improvement](../chapters/02-self-improving-agent-harnesses.md#weakness-mining-routing-and-the-editable-surface) | Named concepts were absent or too brief | Weakness mining, repair routing, editable surface, fixer capability mismatch, safe experiments; held-in/out and miner/guard sections |
| [3 · Building](../chapters/03-building-an-agent-from-scratch.md#trace-a-turn-through-the-implementation) | The execution path and different budget mechanisms needed explanation | Turn sequence diagram; per-item clamp versus history compaction; test receipts and dependency boundaries |
| [4 · Memory](../chapters/04-agent-memory-architecture.md#remembering-a-fact-is-different-from-authorizing-an-action) | Saved history could be confused with current truth or authorization | RAG/memory/context table; dated facts, supersession, scope, and current requests |
| [5 · Coordination](../chapters/05-meta-harness-multi-agent-systems.md#worker-identity-capabilities-and-authority) | Component names alone did not explain their contracts | Package versus role; adapter capabilities; authority intersection; judgment versus bookkeeping |
| [6 · Context](../chapters/06-context-management.md#name-the-failure-and-preserve-the-important-evidence) | Failure names and a concrete preservation example were missing | Poisoning, distraction, confusion, clash; selection and placement; appointment summary |
| [7 · Skills](../chapters/07-agent-skills.md#choosing-a-skill-and-choosing-its-executor) | Activation, execution, and document structure were not distinguished sufficiently | Trigger/non-trigger; disclosure/loading; skill versus executor; evidence beyond a sign-off |
| [8 · Evaluation](../chapters/08-evaluating-ai-agents.md#abstention-fallback-tools-and-partial-progress) | Several measurements needed more practical interpretation | Safe abstention, trajectory diagnosis, fallback gaps, judge calibration, checkpoint grading |
| [9 · Sandboxing](../chapters/09-agent-sandboxing.md#follow-the-attempted-action-to-the-boundary) | A boundary label did not explain the fate of an attempted action | File-read diagram; bad policy scope; local versus remote authority; denied/unavailable/redirected |
| [10 · Testing coordination](../chapters/10-testing-multi-agent-systems.md#place-each-check-where-it-can-enforce-the-rule) | Check placement and insufficient authority needed explicit examples | Before/during/after/promotion table; configuration fingerprints; purpose versus shape; resume revalidation |
| [11 · Engineering improvement](../chapters/11-engineering-self-improvement.md#promotion-requires-more-than-a-passing-score) | Connection to Chapter 2 and remaining source limits were easy to miss | Storage/retrieval/promotion boundaries; actual tool path; failure cleanup; untested behavior |

## What this review does not establish

- Complete spoken coverage, exact quotations, or timestamps for every concept.
- Independent reproduction of the creator’s experiments. Source-reported scores remain attributed to their original experiment; this repository’s inventory evaluation is separate.
- Current behavior of every agent product named by the creator. Product comparisons are dated observations, not permanent specifications.
- A verified line-by-line reconstruction of Chapter 11’s implementation.

## Reading checklist

After each chapter, check whether you can explain the concept in one sentence, trace where it acts in the system, give an ordinary example, name a failure it cannot solve, and identify evidence that would test the claim.

Use the source links at the top of each chapter for the creator’s complete article and available slide decks. The chapter numbers here follow the order in which these videos were added to this repository; they are not the creator’s internal implementation-tag numbers.
