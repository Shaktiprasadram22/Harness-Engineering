"""Terminal UI. Run from the repository root or supply --data."""
import argparse
import json
from pathlib import Path
from .harness import Agent
from .providers import OllamaProvider, ScriptedProvider
from .tools import InventoryTools


def main():
    parser = argparse.ArgumentParser(description="Evidence-backed read-only inventory assistant")
    parser.add_argument("question", nargs="?")
    parser.add_argument("--provider", choices=["scripted", "ollama"], default="scripted")
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument("--endpoint", default="http://localhost:11434")
    parser.add_argument("--data", type=Path, default=Path("data/inventory.csv"))
    parser.add_argument("--session", type=Path)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    provider = ScriptedProvider() if args.provider == "scripted" else OllamaProvider(args.model, args.endpoint)
    try:
        agent = Agent(provider, InventoryTools(args.data))
        if args.session:
            agent.load(args.session)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if not args.question:
        print(f"Inventory agent · {args.provider} · type quit to exit")
        if args.provider == "scripted":
            print("Offline fixture router; this is a harness demo, not an LLM.")
    while True:
        try:
            question = args.question or input("You > ")
        except (EOFError, KeyboardInterrupt):
            break
        if question.strip().lower() in {"quit", "exit"}:
            break
        try:
            result = agent.ask(question)
            print(json.dumps(result, indent=2) if args.json else f"Agent > {result['answer']}")
            if args.session:
                agent.save(args.session)
            if args.trace:
                args.trace.parent.mkdir(parents=True, exist_ok=True)
                with args.trace.open("a") as handle:
                    for event in result["events"]:
                        handle.write(json.dumps(event) + "\n")
        except (ValueError, OSError) as error:
            parser.error(str(error))
        if args.question:
            break


if __name__ == "__main__":
    main()
