"""Repeatable comparisons. Offline runs measure harness behavior, not LLM accuracy."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from inventory_agent.harness import Agent
from inventory_agent.providers import OllamaProvider, ScriptedProvider
from inventory_agent.tools import InventoryTools


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(provider_name, model, endpoint, repeats, dataset, data):
    if repeats < 1:
        raise ValueError("repeats must be positive")
    cases = json.loads(dataset.read_text())
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate eval ID")
    results = {}
    for policy in ("baseline", "improved"):
        attempts = []
        for case in cases:
            for repeat in range(repeats):
                provider = ScriptedProvider() if provider_name == "scripted" else OllamaProvider(model, endpoint)
                result = Agent(provider, InventoryTools(data, policy)).ask(case["question"])
                expected = case["expected"]
                passed = all(result["data"].get(key) == value for key, value in expected.items())
                # Successful factual answers must have real tool evidence as well.
                if expected["status"] == "ok":
                    passed = passed and bool(result["evidence"]) and result["evidence"]["result"]["status"] == "ok"
                attempts.append({"id": case["id"], "group": case["group"], "repeat": repeat,
                                 "passed": bool(passed), "result": result})
        per_item = []
        for case in cases:
            rows = [r for r in attempts if r["id"] == case["id"]]
            n = sum(r["passed"] for r in rows)
            per_item.append({"id": case["id"], "group": case["group"], "passes": n,
                             "attempts": repeats, "pass_at_k": n > 0, "pass_all_k": n == repeats})
        groups = {group: {"passes": sum(r["passed"] for r in attempts if r["group"] == group),
                          "attempts": sum(r["group"] == group for r in attempts)} for group in ("miner", "guard")}
        results[policy] = {"passes": sum(r["passed"] for r in attempts), "attempts": len(attempts),
                           "groups": groups, "items": per_item, "runs": attempts}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    source = {str(p): fingerprint(p) for p in sorted(Path("inventory_agent").glob("*.py"))}
    source["evals/run.py"] = fingerprint(Path(__file__))
    return {"generated_at": datetime.now(timezone.utc).isoformat(), "provider": provider_name,
            "model": model if provider_name == "ollama" else "fixture-router-v1",
            "scope": "offline deterministic harness checks" if provider_name == "scripted" else "live local model evaluation",
            "dataset_sha256": fingerprint(dataset), "data_sha256": fingerprint(data),
            "source_sha256": source, "git_commit": commit.stdout.strip(),
            "working_tree_dirty": bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()),
            "repeats": repeats, "results": results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=["scripted", "ollama"], default="scripted")
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument("--endpoint", default="http://localhost:11434")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, default=Path("artifacts/evaluation.json"))
    args = parser.parse_args()
    try:
        report = run(args.provider, args.model, args.endpoint, args.repeats,
                     Path("evals/cases.json"), Path("data/inventory.csv"))
    except (ValueError, OSError) as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(report["scope"])
    for policy, result in report["results"].items():
        print(f"{policy}: {result['passes']}/{result['attempts']} passed; {result['groups']}")
    print(f"Full per-item evidence: {args.output}")


if __name__ == "__main__":
    main()
