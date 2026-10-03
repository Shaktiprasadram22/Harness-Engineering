# Harness Engineering

### A working inventory agent, reproducible evaluations, and eleven study chapters

This repository combines an implemented Python agent harness with a study guide to the infrastructure around AI models. The inventory assistant demonstrates read-only tools, conversation persistence, evidence-backed answers, explicit branch selection, and a bounded action loop.

## Run it in one minute

Python 3.11+; run these commands from the repository root. The offline demo uses only the standard library.

```sh
git clone https://github.com/Shaktiprasadram22/Harness-Engineering.git
cd Harness-Engineering
python -m inventory_agent.cli "How many blue notebooks at north?"
python -m inventory_agent.cli "How many blue notebooks?"
python -m unittest discover -s tests -v
python -m evals.run
```

```text
Agent > blue notebook at north: 7 in stock.
Agent > Which branch: central or north? Or all branches?
```

**Offline mode uses a scripted test provider, not an LLM.** For a real model, use the Ollama adapter:

```sh
ollama pull qwen3:4b
python -m inventory_agent.cli --provider ollama --model qwen3:4b
```

Install/start Ollama separately and use a tool-capable model. The adapter was exercised against a real local Qwen3 0.6B Q8_0 model. [Live evaluation and reproducibility](docs/live-evaluation.md) cover the measured results and limitations.

## What is implemented

| Capability | Implementation |
| :--- | :--- |
| Model interface | Real Ollama HTTP adapter plus an offline test double |
| Read-only inventory | Three allowlisted tools over an immutable synthetic snapshot |
| Guardrail | Unknown/mutation tools denied; branch guesses rejected or clarified |
| Grounding | Final factual answers rendered from tool results with inspectable evidence |
| Conversation | Bounded history, atomic session saves, and reload |
| Failure handling | Request timeout, bounded attempts, malformed-output handling |
| Evaluation | Offline checks plus 16 live development and six reserved transfer scenarios, three repeats, per-case evidence and fingerprints |
| Verification | Unit/integration tests and GitHub Actions on Python 3.11/3.12 |

## Measured improvement

A deliberate baseline defaults ambiguous queries to Central. The improved harness requires an explicit branch.

| Offline harness comparison | Baseline | Improved |
| :--- | ---: | ---: |
| Missing-branch cases | 0/9 | 9/9 |
| Regression guards | 27/27 | 27/27 |
| **All attempts** | **27/36** | **36/36** |

These are deterministic harness checks, not LLM accuracy or a held-out benchmark. [Read the experiment and limitations](docs/evaluation.md) or inspect the [full results](docs/results/offline-evaluation.json).

The real Qwen3 0.6B development comparison improved whole-scenario passes from **18/48 to 30/48** and individual turns from **21/60 to 42/60**. Reserved transfer passes improved from **3/18 to 9/18**. Live multi-turn development scenarios still failed **0/12** before and after. [See full live results and limitations](docs/live-evaluation.md); these are separate from the deterministic scores above.

## Explore the implementation

- [Setup, architecture, demo, and limitations](docs/implementation.md)
- [Agent harness](inventory_agent/harness.py)
- [Read-only tool executor](inventory_agent/tools.py)
- [Model adapters](inventory_agent/providers.py)
- [Tests](tests/test_agent.py)
- [Evaluation cases](evals/cases.json)

The code does not claim an OS sandbox or production readiness. It deliberately supports a narrow querying contract so its behavior is easy to inspect and test.

## Chapters

| Chapter | Topic | What you will learn |
| :--- | :--- | :--- |
| **01** | [The System Around the Model](chapters/01-the-system-around-the-model.md) | The ten parts of an agent harness, illustrated through a login-bug investigation |
| **02** | [Self-Improving Agent Harnesses](chapters/02-self-improving-agent-harnesses.md) | Improvement loops, controlled experiments, regression checks, and reviewable changes |
| **03** | [Building an AI Agent From Scratch](chapters/03-building-an-agent-from-scratch.md) | Python sketches, tool loops, persistence, verification, and architecture |
| **04** | [Agent Memory Architecture](chapters/04-agent-memory-architecture.md) | Four memory types, context assembly, conflict resolution, and forgetting |
| **05** | [Meta-Harness: Coordinating Multiple Agents](chapters/05-meta-harness-multi-agent-systems.md) | Team coordination, eight components, evidence, and failure recovery |
| **06** | [Context Management](chapters/06-context-management.md) | Select, compress, write, isolate, and inspect the model’s working context |
| **07** | [Agent Skills](chapters/07-agent-skills.md) | Reusable procedures, selective loading, evidence, and practical evaluation |
| **08** | [Evaluating AI Agents](chapters/08-evaluating-ai-agents.md) | Metrics, repeated trials, evidence, and measured improvements |
| **09** | [Agent Sandboxing](chapters/09-agent-sandboxing.md) | Isolation layers, access boundaries, credentials, and blast radius |
| **10** | [Testing Multi-Agent Systems](chapters/10-testing-multi-agent-systems.md) | Verified evidence, output contracts, recovery, and final-revision checks |
| **11** | [Engineering a Self-Improving Agent](chapters/11-engineering-self-improvement.md) | Output strategies, temporary storage, reachability, and adoption |

## About these notes

**Coverage:** [Review of all eleven chapters](docs/chapter-coverage.md) lists the expanded explanations and remaining source limitations. These are study guides, not certified complete video transcripts.

These chapters are original educational explanations inspired by **The Carbon Layer’s videos and companion articles**. It is not a transcript. Examples and diagrams were created for this guide.

- [Watch the masterclass](https://www.youtube.com/watch?v=mQfTdNVCOB0)
- [Read the creator’s companion article](https://www.thecarbonlayer.com/harness-engineering/)
- [Explore the playlist](https://www.youtube.com/playlist?list=PLegY0xEsc4pT70SoWjgeBcRCc7eXtgpx0)

- [Watch the Chapter 2 video](https://www.youtube.com/watch?v=KoDohnhLpJM)
- [Read the Chapter 2 companion article](https://www.thecarbonlayer.com/self-evolving-harness/)

- [Watch the Chapter 3 video](https://www.youtube.com/watch?v=oUBgqzcV1qw)
- [Explore the original Carbon implementation](https://github.com/thecarbonlayer/carbon)

- [Watch the Chapter 4 video](https://www.youtube.com/watch?v=PxuMqeIqCEo)
- [Read the Chapter 4 companion article](https://www.thecarbonlayer.com/agent-memory-architecture/)

- [Watch the Chapter 5 video](https://www.youtube.com/watch?v=HRUBDPdvaHU)
- [Read the Chapter 5 companion article](https://thecarbonlayer.com/meta-harness/)

- [Watch the Chapter 6 video](https://www.youtube.com/watch?v=mM_Wxemh3lU)
- [Read the Chapter 6 companion article](https://www.thecarbonlayer.com/context-management/)

- [Watch the Chapter 7 video](https://www.youtube.com/watch?v=nrh1YtPKRD0)
- [Read the Chapter 7 companion article](https://thecarbonlayer.com/agent-skills/)

- [Watch the Chapter 8 video](https://www.youtube.com/watch?v=B9NPE_CaK5Q)
- [Read the Chapter 8 companion article](https://www.thecarbonlayer.com/agent-evaluation/)

- [Watch the Chapter 9 video](https://www.youtube.com/watch?v=-01_NB4SbBY)
- [Read the Chapter 9 companion article](https://www.thecarbonlayer.com/agent-sandboxing/)

- [Watch the Chapter 10 video](https://www.youtube.com/watch?v=RSOQ0lQ2-1M)
- [Read the Chapter 10 companion article](https://www.thecarbonlayer.com/meta-harness-build/)

- [Watch the Chapter 11 video](https://www.youtube.com/watch?v=qDJIEodb2tk)
