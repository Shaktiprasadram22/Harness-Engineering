"""Live Ollama evaluation with conversation scenarios and before/after evidence.

The grader never sends expected values to the provider. Use --variant before
for the frozen v1 harness; --variant after uses the current implementation.
"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import statistics
import subprocess
import time
import urllib.request
from inventory_agent.harness import Agent
from inventory_agent.providers import OllamaProvider
from inventory_agent.tools import InventoryTools
from evals.baselines.harness_v1 import Agent as BeforeAgent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def grade(result, expected):
    for key, value in expected.items():
        actual = result["data"].get("status" if key == "status_in" else key)
        if key == "status_in":
            if actual not in value:
                return False
        elif actual != value:
            return False
    if result["status"] == "ok":
        return bool(result["evidence"]) and result["evidence"]["result"]["status"] == "ok"
    return True


class Recorder:
    def __init__(self, provider):
        self.provider = provider
        self.calls = []

    def chat(self, messages, tools):
        started = time.monotonic()
        record = {"messages": copy.deepcopy(messages), "tools": copy.deepcopy(tools)}
        try:
            response = self.provider.chat(messages, tools)
            record["response"] = response
            record["metrics"] = dict(self.provider.last_metrics)
            return response
        finally:
            record["elapsed_ms"] = round((time.monotonic() - started) * 1000, 3)
            self.calls.append(record)


def server_info(endpoint, model):
    def request(path):
        with urllib.request.urlopen(endpoint.rstrip("/") + path, timeout=20) as response:
            return json.load(response)
    version, tags = request("/api/version"), request("/api/tags")
    matches = [item for item in tags["models"] if item["name"] == model or item.get("model") == model]
    if not matches:
        raise ValueError("Requested model is not installed on the evaluation server")
    return {"version": version, "model": matches[0]}


def summary(attempts):
    rows = []
    for case_id in dict.fromkeys(attempt["id"] for attempt in attempts):
        cases = [attempt for attempt in attempts if attempt["id"] == case_id]
        rows.append({"id": case_id, "group": cases[0]["group"],
                     "passes": sum(case["passed"] for case in cases), "attempts": len(cases),
                     "pass_at_k": any(case["passed"] for case in cases),
                     "pass_all_k": all(case["passed"] for case in cases)})
    turns = [turn for attempt in attempts for turn in attempt["turns"]]
    calls = [call for attempt in attempts for call in attempt["model_calls"]]
    latency = [call["elapsed_ms"] for call in calls]
    return {"scenario_passes": sum(attempt["passed"] for attempt in attempts),
            "scenario_attempts": len(attempts), "turn_passes": sum(turn["passed"] for turn in turns),
            "turn_attempts": len(turns), "items": rows,
            "model_calls": len(calls),
            "prompt_tokens": sum((call.get("metrics", {}).get("prompt_eval_count") or 0) for call in calls),
            "generated_tokens": sum((call.get("metrics", {}).get("eval_count") or 0) for call in calls),
            "median_model_call_ms": round(statistics.median(latency), 3) if latency else None,
            "max_model_call_ms": round(max(latency), 3) if latency else None}


def evaluate(variant, model, endpoint, dataset, repeats, output, case_ids=None):
    if repeats < 1:
        raise ValueError("repeats must be positive")
    cases = json.loads(dataset.read_text())
    if case_ids:
        cases = [case for case in cases if case["id"] in case_ids]
    if not cases:
        raise ValueError("No cases selected")
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate scenario ID")
    source_paths = [*Path("inventory_agent").glob("*.py"), Path("evals/live.py"),
                    Path("evals/baselines/harness_v1.py")]
    report = {"generated_at": datetime.now(timezone.utc).isoformat(), "variant": variant,
              "provider": "ollama", "model": model, "server": server_info(endpoint, model),
              "generation": {"temperature": 0, "think": False, "num_predict": 256,
                             "num_ctx": 4096, "num_thread": 4, "seeds": list(range(42, 42 + repeats))},
              "dataset": str(dataset), "dataset_sha256": digest(dataset),
              "data_sha256": digest("data/inventory.csv"),
              "source_sha256": {str(path): digest(path) for path in sorted(source_paths)},
              "platform": {"python": platform.python_version(), "system": platform.system(),
                           "machine": platform.machine()},
              "git_commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
              "working_tree_dirty": bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip()),
              "repeats": repeats, "attempts": []}
    agent_type = BeforeAgent if variant == "before" else Agent
    output.parent.mkdir(parents=True, exist_ok=True)
    for case in cases:
        for repeat in range(repeats):
            recorder = Recorder(OllamaProvider(model, endpoint, timeout=90, seed=42 + repeat))
            agent = agent_type(recorder, InventoryTools(Path("data/inventory.csv")))
            turns = []
            for turn in case["turns"]:
                result = agent.ask(turn["question"])
                turns.append({"question": turn["question"], "expected": turn["expected"],
                              "passed": grade(result, turn["expected"]), "result": result})
            attempt = {"id": case["id"], "group": case["group"], "repeat": repeat,
                       "passed": all(turn["passed"] for turn in turns),
                       "turns": turns, "model_calls": recorder.calls}
            report["attempts"].append(attempt)
            report["summary"] = summary(report["attempts"])
            output.write_text(json.dumps(report, indent=2) + "\n")
            print(f"{variant} {case['id']} repeat {repeat + 1}: {'PASS' if attempt['passed'] else 'FAIL'}", flush=True)
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["summary"], indent=2), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["before", "after"], required=True)
    parser.add_argument("--model", default="qwen3:0.6b")
    parser.add_argument("--endpoint", default="http://localhost:11434")
    parser.add_argument("--dataset", type=Path, default=Path("evals/live-development.json"))
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", action="append")
    args = parser.parse_args()
    evaluate(args.variant, args.model, args.endpoint, args.dataset, args.repeats, args.output, args.case)


if __name__ == "__main__":
    main()
