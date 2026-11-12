"""Falsify the response checker with observable contract violations."""

import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("evaluation", ROOT / "scripts/evaluate.py")
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
        self.responses = json.loads((ROOT / "evals/results/2026-11-11.json").read_text(encoding="utf-8"))
        self.case = self.cases[0]
        self.response = self.responses[self.case["id"]]

    def test_recorded_outputs_satisfy_observable_contract(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(evaluation.grade(case, self.responses[case["id"]]), [])

    def test_rejects_wrong_host_extra_goal_missing_constraint_and_invented_check(self):
        mutations = [
            self.response.replace("/goal ", "", 1),
            self.response + "\n```text\n/goal Another condition\n```",
            self.response.replace("Do not modify files outside src/auth", "Change any files"),
            self.response.replace("python -m unittest discover -s tests/auth", "npm test"),
            "```text\n/goal " + "x" * 4000 + "\n```",
        ]
        for response in mutations:
            with self.subTest(response=response[:100]):
                self.assertTrue(evaluation.grade(self.case, response))

    def test_vague_task_requires_only_one_question(self):
        case = next(case for case in self.cases if case.get("question"))
        self.assertEqual(evaluation.grade(case, evaluation.QUESTION), [])
        self.assertTrue(evaluation.grade(case, evaluation.QUESTION + " Also, what tests?"))


if __name__ == "__main__":
    unittest.main()
