# Write Goal — directory submission packet

Prepared for version 0.3.0. This packet is a reviewable draft; no directory
submission, publisher verification, or policy attestation has been completed.
The maintained source remains [edcadet10/write-goal](https://github.com/edcadet10/write-goal).

## Listing

| Field | Prepared value |
| --- | --- |
| Identifier | `write-goal` |
| Display name | Write Goal |
| Publisher named in package | Ed Cadet — [edcadet10](https://github.com/edcadet10) |
| Subtitle | A finish line you can prove |
| Category | Productivity |
| Source and website | [GitHub repository](https://github.com/edcadet10/write-goal) |
| Support | [GitHub issues](https://github.com/edcadet10/write-goal/issues) |
| License | MIT |
| Icon | Square 512 × 512 PNG; source SVG and PNG included |

The complete listing description and starter prompts are in
[the Codex manifest](../.codex-plugin/plugin.json). The Claude manifest uses
the same package identity, version, and publisher. The listing does not claim
an official endorsement, a ranking, or guaranteed task completion.

## What a reviewer can verify

Write Goal drafts a single completion condition with a measurable end state,
observable proof, preserved constraints, and a stopping boundary. Claude Code
receives a `/goal` prefix; Codex receives plain completion text. Unknown checks
remain placeholders. Drafting does not activate a goal or schedule future work.

The package declares no MCP servers, hooks, external service, or plugin sign-in.
Model access and tool permissions belong to the host. The included instructions
can read available project context to ground a draft, so users should follow
their host's data and workspace policies.

The [behavioral evaluation record](../evals/results/2026-11-11.md) includes actual
fictional drafting outputs and observed corrections. The native installation
checks use real clients with temporary profiles. Those checks do not establish
model behavior in every host; live Claude model inference remains unverified
because the available local credential returned 401.

## Package and checks

Run `python scripts/build_plugin.py --output /path/outside/checkout/write-goal-plugin.zip`
from the repository. Choose a writable output path outside the checkout.
The ZIP and SHA-256 checksum are generated together. Its explicit file list
includes the host manifests, complete skill, icon assets, MIT license, and
package README. Development scripts, caches, repository metadata, and unrelated
files are excluded. The source is [build_plugin.py](../scripts/build_plugin.py).

The archive is for skills-only upload or manual distribution. The GitHub-hosted
catalog remains the native installation route. Required checks are the portable
test suite, cold native installs, complete package-content comparison, and
`claude plugin validate --strict --profile directory .`.

## External steps still required

- Explicit authorization to submit to either directory, including any packaged
  copy uploaded for review.
- Anthropic: an eligible paid account, connected GitHub account with push access,
  portal validation, name availability, and the publisher's policy attestations.
- OpenAI: an eligible verified developer identity, upload validation, and the
  publisher's policy attestations. This is a skills-only package; no MCP review
  account or fabricated connector demonstration is supplied.
- Review decisions and any final publication step must be verified in the
  respective portal. Local checks are not approval or proof that the name is
  available. Do not describe this packet as submitted, approved, or listed.

## Official references

- [Anthropic submission](https://claude.com/docs/plugins/submit) and
  [pre-submission checks](https://claude.com/docs/plugins/pre-submission-checklist).
- [OpenAI upload and review](https://developers.openai.com/plugins/deploy/submission),
  including skills-only requirements and listing metadata.
