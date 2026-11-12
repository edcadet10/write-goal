# Contributing

Thanks for helping make `write-goal` sharper and easier to trust. Documentation,
portable installer fixes, adversarial examples, and focused skill improvements
are welcome.

The shared workflow and documentation are AI-agnostic. Contributors may use
their chosen assistant or work without AI; no model provider is required.

## Start here

- Open a focused pull request directly for a small fix.
- Use an [issue form](https://github.com/edcadet10/write-goal/issues/new/choose) for a reproducible bug or feature proposal.
- Explain changes to host behavior or the core output contract in the PR, including compatibility and behavioral evidence.
- Report vulnerabilities through [GitHub's private reporting form](https://github.com/edcadet10/write-goal/security/advisories/new), never a public issue.

You do not need an assignment for an unclaimed small issue. Comment before
starting larger work so contributors do not duplicate effort. Draft pull
requests are welcome.

## Validate your change

The repository needs Python 3.10+; it has no package-install step. Bash is
optional for the compatibility entrypoints.

```bash
python scripts/check.py
```

The check validates skill structure, repository links, the SVG banner, and
isolated installations for both hosts. CI also checks Bash syntax and runs
the suite on Windows, macOS, and Linux with Python 3.10 and 3.12.

### Optional application-adapter checks

For changes to native adapter packaging, also run the corresponding real clients in isolated
temporary profiles (requires Claude Code and Codex CLI on your PATH):

```bash
claude plugin validate --strict .
python scripts/check_plugins.py
```

The native smoke test installs from the checkout, checks the host inventory,
and compares the installed package content with the source after normalizing
text line endings. It does not invoke a
model. Use `--claude` or `--codex` to provide a client path when needed.
To test a GitHub branch before merging, add
`--source edcadet10/write-goal --ref <branch>`.

For directory packaging, use `python scripts/build_plugin.py --output <path.zip>`
with a destination outside the checkout. The build includes only an explicit
file list and creates a checksum. Review the
[submission packet](distribution/SUBMISSION.md) before any external submission.
An archive build or a local directory check does not submit or approve a plugin.

The listing icon is maintained in `assets/icon.svg`; its 512-pixel PNG is a
rendered copy of that vector. Rendering is a maintainer operation, separate from
the installer and dependency-free package checks.

For behavior changes, include at least two fictional examples in the pull
request:

- one rough task that should produce a goal;
- one vague task that should trigger exactly one clarifying question.

Show the actual generated condition for the first example and name the host.
Use the [evaluation guide](evals/README.md) for broader behavior changes. Model
outputs need semantic review; text matching alone does not prove correctness.
An independent evaluator can be any suitable assistant or reviewer. The named
applications in a case identify its formatting target, not the evaluator's
required model or provider.

## Design guardrails

- Keep shared instructions provider-neutral. Select optional formatting by the destination application, not the model brand.
- Emit exactly one copy-paste condition; explicit plain text overrides a native wrapper.
- Keep output under 4,000 characters as a portable default and respect stricter known application limits.
- Require transcript-visible proof, not a check the evaluator must run itself.
- Preserve explicit constraints and the user's stopping boundary; do not confuse a cap or deadline with success.
- Prefer actual project commands when they can be discovered cheaply.
- Keep the skill concise and avoid new runtime dependencies without a concrete need.
- Never add private prompts, credentials, or proprietary workspace data as examples.

Keep pull requests focused on one concern. Link the relevant issue and explain
the user-visible effect, compatibility impact, and rollback path.

Participation follows the [Code of Conduct](CODE_OF_CONDUCT.md).
