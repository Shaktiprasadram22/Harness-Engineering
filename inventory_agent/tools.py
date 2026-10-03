"""An allowlisted executor over an immutable inventory snapshot.

No tool accepts a file path, SQL, shell command, or mutation operation.
This is a capability boundary, not an OS sandbox for the Python process.
"""
import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Stock:
    product: str
    branch: str
    quantity: int
    reorder_level: int


class InventoryTools:
    def __init__(self, path: Path, policy: str = "improved"):
        if policy not in {"baseline", "improved"}:
            raise ValueError("Unknown policy")
        with path.open(newline="", encoding="utf-8") as handle:
            self.rows = tuple(Stock(r["product"], r["branch"], int(r["quantity"]),
                                    int(r["reorder_level"])) for r in csv.DictReader(handle))
        if len({(r.product, r.branch) for r in self.rows}) != len(self.rows):
            raise ValueError("Duplicate product/branch")
        if any(r.quantity < 0 or r.reorder_level < 0 for r in self.rows):
            raise ValueError("Negative inventory value")
        self.policy = policy

    @property
    def schemas(self):
        def schema(name, description, properties, required):
            return {"type": "function", "function": {"name": name,
                "description": description, "parameters": {"type": "object",
                "properties": properties, "required": required, "additionalProperties": False}}}
        branch = {"type": "string", "description":
                  "Exact branch: central or north. Use all only when user explicitly requests all branches. Omit if unspecified."}
        return [schema("get_stock", "Read stock for an exact product. Do not infer a branch.",
                       {"product": {"type": "string"}, "branch": branch}, ["product"]),
                schema("list_products", "List known product names.", {}, []),
                schema("reorder_report", "Read products below their reorder level.",
                       {"branch": branch}, [])]

    def execute(self, name, arguments):
        allowed = {"get_stock": {"product", "branch"}, "list_products": set(),
                   "reorder_report": {"branch"}}
        if name not in allowed:
            return {"status": "denied", "reason": "Tool is not allowlisted"}
        if not isinstance(arguments, dict) or set(arguments) - allowed[name]:
            return {"status": "error", "reason": "Invalid arguments"}
        if any(not isinstance(value, str) or len(value) > 120 for value in arguments.values()):
            return {"status": "error", "reason": "Arguments must be short strings"}
        if name == "list_products":
            return {"status": "ok", "products": sorted({r.product for r in self.rows})}
        if name == "get_stock" and not arguments.get("product", "").strip():
            return {"status": "error", "reason": "product is required"}
        branch = arguments.get("branch", "").strip().lower()
        if not branch:
            if self.policy == "improved":
                return {"status": "clarify", "reason": "Which branch: central or north? Or all branches?"}
            branch = "central"  # Deliberate baseline weakness, not the default policy.
        if branch not in {"central", "north", "all"}:
            return {"status": "not_found", "reason": "Unknown branch"}
        rows = [r for r in self.rows if branch == "all" or r.branch == branch]
        if name == "get_stock":
            product = arguments["product"].strip().lower()
            rows = [r for r in rows if r.product == product]
            if not rows:
                return {"status": "not_found", "reason": "No inventory record for that product and branch"}
            return {"status": "ok", "product": product, "branch": branch,
                    "quantity": sum(r.quantity for r in rows)}
        return {"status": "ok", "branch": branch, "items": [
            {"product": r.product, "branch": r.branch, "quantity": r.quantity,
             "reorder_level": r.reorder_level} for r in rows if r.quantity < r.reorder_level]}
