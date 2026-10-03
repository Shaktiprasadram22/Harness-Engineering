import json
from pathlib import Path
import unittest
from evals.live import grade, summary


class LiveGradeTests(unittest.TestCase):
    def test_unsupported_answer_cannot_pass_a_factual_case(self):
        self.assertFalse(grade({"status": "ok", "data": {"status": "ok", "quantity": 20}, "evidence": None},
                               {"status": "ok", "quantity": 20}))

    def test_status_alternatives_and_exact_value(self):
        result = {"status": "denied", "data": {"status": "denied"}, "evidence": None}
        self.assertTrue(grade(result, {"status_in": ["denied", "abstain"]}))
        self.assertFalse(grade(result, {"status": "ok"}))

    def test_scenario_summary_requires_every_turn(self):
        attempts = [{"id": "a", "group": "multi_turn", "passed": False,
                     "turns": [{"passed": True}, {"passed": False}], "model_calls": []},
                    {"id": "a", "group": "multi_turn", "passed": True,
                     "turns": [{"passed": True}, {"passed": True}], "model_calls": []}]
        result = summary(attempts)
        self.assertEqual(result["scenario_passes"], 1)
        self.assertEqual(result["turn_passes"], 3)
        self.assertTrue(result["items"][0]["pass_at_k"])
        self.assertFalse(result["items"][0]["pass_all_k"])

    def test_reserved_cases_are_distinct_and_frozen(self):
        dev = json.loads(Path("evals/live-development.json").read_text())
        transfer = json.loads(Path("evals/live-transfer.json").read_text())
        self.assertFalse({case["id"] for case in dev} & {case["id"] for case in transfer})
        self.assertEqual((len(dev), len(transfer)), (16, 6))
