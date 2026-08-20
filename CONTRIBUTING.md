# Contributing

Thanks for helping make `write-goal` sharper and easier to trust. Documentation,
portable installer fixes, adversarial examples, and focused skill improvements
are welcome.

## Start here

- Open a focused pull request directly for a small fix.
- Use an [issue form](https://github.com/edcadet10/write-goal/issues/new/choose) for a reproducible bug or feature proposal.
- Start a [Discussion](https://github.com/edcadet10/write-goal/discussions) before changing the skill's core output contract.
- Report vulnerabilities through [GitHub's private reporting form](https://github.com/edcadet10/write-goal/security/advisories/new), never a public issue.

You do not need an assignment for an unclaimed small issue. Comment before
starting larger work so contributors do not duplicate effort. Draft pull
requests are welcome.

## Validate your change

The repository needs Bash and Python 3; it has no package-install step.

```bash
./scripts/check.sh
```

The check validates the skill metadata, repository links, SVG banner, shell
syntax, and a repeatable clean-room install under a temporary Claude directory.

For behavior changes, include at least two fictional examples in the pull
request:

- one rough task that should produce a goal;
- one vague task that should trigger exactly one clarifying question.

Show the generated `/goal` line for the first example.

## Design guardrails

- Emit exactly one copy-paste `/goal` condition.
- Keep output below Claude Code's 4,000-character goal limit.
- Require transcript-visible proof, not a check the evaluator must run itself.
- Preserve explicit constraints and a finite turn cap.
- Prefer actual project commands when they can be discovered cheaply.
- Keep the skill concise and avoid new runtime dependencies without a concrete need.
- Never add private prompts, credentials, or proprietary workspace data as examples.

Keep pull requests focused on one concern. Link the relevant issue and explain
the user-visible effect, compatibility impact, and rollback path.

Participation follows the [Code of Conduct](CODE_OF_CONDUCT.md).
