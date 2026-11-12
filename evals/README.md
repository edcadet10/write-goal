# Behavioral evaluation

The evaluation protocol is provider-neutral. Use an independent assistant or
reviewer of your choice; no named AI service is required. Case application names
select expected output formatting, not the evaluator's model provider.

Package CI cannot establish whether a model follows a skill. These fourteen
fictional requests exercise known and unknown checks, vague or missing tasks,
host selection, exact constraints, changing queues, external deadlines, human
approval, invented acceptance criteria, a generic assistant, and the distinction
between a model provider and its destination application.

Give an independent evaluator the skill and only the `id`, `host`, `request`,
and `context` fields from [cases.json](cases.json). Treat every case as a fresh
session. Do not show the grading fields or a desired answer. The evaluator
must draft only, with no task execution, goal activation, or external writes.
Save the complete actual responses as a JSON object mapping IDs to strings.

```bash
python scripts/evaluate.py --responses /path/to/responses.json
```

The checker tests observable formatting and selected requirements. Review the
responses independently for proof coverage, command provenance, scope,
constraints, the difference between a deadline and achievement, and unauthorized
activation. Passing string checks alone is insufficient. Never rewrite an
evaluation response to make it pass; fix the skill and rerun affected cases.

Record the skill revision, model/host when known, actual responses, reviewer
observations, and failures in the PR. No ranking claim follows from this small
suite. Add cases for demonstrated failures instead of growing a speculative
catalog. Use only fictional or explicitly shareable data.

The [2026-11-11 record](results/2026-11-11.md) preserves the observed failures,
corrections, raw outputs, and final affected-case retests.
The [2026-11-12 record](results/2026-11-12.md) covers the provider-neutral shared
workflow and optional application adapters.
Those historical records identify the tools actually used in their runs. They
do not make those tools prerequisites for later evaluations.
