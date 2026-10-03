"""A real Ollama adapter and a deterministic test double.

ScriptedProvider tests the harness. Its outputs are not LLM measurements.
"""
import json
import re
import urllib.error
import urllib.request


class ProviderError(RuntimeError):
    pass


class OllamaProvider:
    name = "ollama"

    def __init__(self, model="qwen3:4b", endpoint="http://localhost:11434", timeout=60,
                 seed=42, max_tokens=256, thinking=False):
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self.seed, self.max_tokens, self.thinking = seed, max_tokens, thinking
        self.last_metrics = {}

    def chat(self, messages, tools):
        payload = {"model": self.model, "messages": messages, "tools": tools,
                   "stream": False, "think": self.thinking,
                   "options": {"temperature": 0, "seed": self.seed, "num_predict": self.max_tokens,
                               "num_ctx": 4096, "num_thread": 4}}
        request = urllib.request.Request(self.endpoint + "/api/chat",
            data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.load(response)
            self.last_metrics = {key: body.get(key) for key in (
                "total_duration", "load_duration", "prompt_eval_count", "prompt_eval_duration",
                "eval_count", "eval_duration", "done_reason")}
            message = body["message"]
            if not isinstance(message, dict):
                raise ValueError("Invalid message")
            return message
        except (urllib.error.URLError, TimeoutError, OSError, ValueError, KeyError) as error:
            raise ProviderError("Model request failed; check Ollama, the model name, and endpoint") from error


class ScriptedProvider:
    """Small fixture router for a documented subset of English; not an AI model."""
    name = "scripted"
    model = "fixture-router-v1"

    def chat(self, messages, tools):
        current = next(m["content"] for m in reversed(messages) if m["role"] == "user").lower()
        if re.search(r"\b(delete|remove|update|write|password|secret|weather|ignore)\b", current):
            return {"role": "assistant", "content": "I cannot perform that request."}
        branch = next((b for b in ("central", "north") if re.search(r"\b" + b + r"\b", current)), None)
        if "all branches" in current:
            branch = "all"
        # A documented context-dependent follow-up used by the demo.
        if current.strip() in {"and north?", "and central?"}:
            earlier = " ".join(m["content"].lower() for m in messages[:-1] if m["role"] == "user")
            current += " " + earlier
        known = next((p for p in ("blue notebook", "black pen", "red folder", "purple stapler")
                      if p in current), None)
        if "list" in current and "product" in current:
            name, args = "list_products", {}
        elif "reorder" in current:
            name, args = "reorder_report", {}
        elif known:
            name, args = "get_stock", {"product": known}
        else:
            return {"role": "assistant", "content": "Please specify an inventory question."}
        if branch and name != "list_products":
            args["branch"] = branch
        return {"role": "assistant", "content": "", "tool_calls": [
            {"function": {"name": name, "arguments": args}}]}
