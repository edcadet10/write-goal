# Repository maintenance

- Keep the shared skill provider-neutral. Put application-specific syntax and
  activation behavior in `skills/write-goal/references/hosts.md`.
- Keep common documentation usable without a particular AI vendor or native
  client. Label adapter requirements and historical test environments clearly;
  preserve the factual provenance of recorded evidence.
- Make code changes through tested GitHub pull requests. GitHub is the maintained
  source of truth.
- Use the authenticated owner's established Git identity for work they authorize.
  Do not add AI tools as authors, committers, or co-authors. Preserve genuine
  human attribution; do not reassign another person's contribution.
- Run `python scripts/check.py`. For skill or adapter changes, also review actual
  drafting outputs and run the native installation smoke checks in isolated
  profiles. Package every resource referenced by the skill.
