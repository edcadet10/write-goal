#!/usr/bin/env python3
"""Check observable draft invariants in real model responses; no model/API calls.

Input: a JSON object mapping case IDs to complete response strings. This checks
format, command provenance samples, and explicit requirements, not all semantics.
"""

import argparse
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
QUESTION = "What concrete state should be true when this is finished?"


def grade(case: dict, response: str) -> list[str]:
    errors = []
    if case.get("question"):
        return [] if response.strip() == QUESTION else ["Expected only the clarification question"]
    blocks = list(re.finditer(r"```(?:text)?\s*\n(.*?)\n```", response, re.DOTALL))
    if len(blocks) != 1:
        return ["Expected exactly one fenced goal block"]
    block = blocks[0]
    goal = block.group(1).strip()
    if len(goal.splitlines()) != 1 or not goal:
        errors.append("Expected a single nonempty goal line")
    if len(goal) >= 4000:
        errors.append("Goal must be under 4,000 characters")
    if goal.startswith("/goal ") != (case["host"] == "claude"):
        errors.append("Wrong host syntax")
    outside = response[:block.start()] + response[block.end():]
    if len([line for line in outside.splitlines() if line.strip()]) > 2:
        errors.append("More than two commentary lines")
    for required in case.get("required", []):
        if required.casefold() not in goal.casefold():
            errors.append(f"Missing explicit requirement: {required}")
    for forbidden in case.get("forbidden", []):
        if forbidden.casefold() in goal.casefold():
            errors.append(f"Unexpected content: {forbidden}")
    for alternatives in case.get("required_any", []):
        if not any(value.casefold() in goal.casefold() for value in alternatives):
            errors.append(f"Missing requirement expressed as one of: {alternatives}")
    placeholders = re.findall(r"<[^>\n]+>", goal)
    if case.get("placeholder") is True and not placeholders:
        errors.append("Unknown verification requires a visible placeholder")
    if case.get("placeholder") is False and placeholders:
        errors.append("Known verification should not require a placeholder")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", required=True, type=Path)
    args = parser.parse_args()
    cases = json.loads((ROOT / "evals/cases.json").read_text(encoding="utf-8"))
    responses = json.loads(args.responses.read_text(encoding="utf-8"))
    failed = 0
    for case in cases:
        response = responses.get(case["id"])
        errors = ["Missing response string"] if not isinstance(response, str) else grade(case, response)
        print(f"{'FAIL' if errors else 'PASS'} {case['id']}" + (": " + "; ".join(errors) if errors else ""))
        failed += bool(errors)
    print(f"{len(cases) - failed}/{len(cases)} cases pass deterministic checks; semantic review is still required.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
