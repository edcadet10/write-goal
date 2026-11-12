<p align="center">
  <img src="assets/banner.svg" alt="write-goal — AI-agnostic goal writing with observable proof." width="100%">
</p>

<p align="center">
  <a href="https://github.com/edcadet10/write-goal/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/edcadet10/write-goal/ci.yml?branch=main&amp;style=flat-square&amp;label=CI" alt="CI status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-4ecca3?style=flat-square" alt="MIT license"></a>
  <img src="https://img.shields.io/badge/instructions-AI%20agnostic-4ecca3?style=flat-square" alt="AI-agnostic instructions">
  <a href="https://code.claude.com/docs/en/skills"><img src="https://img.shields.io/badge/Claude%20Code-compatible-7c5cff?style=flat-square" alt="Claude Code compatible"></a>
  <a href="https://learn.chatgpt.com/docs/build-skills"><img src="https://img.shields.io/badge/Codex-compatible-4ecca3?style=flat-square" alt="Codex compatible"></a>
</p>

<p align="center"><b>One measurable goal, with the evidence needed to prove it.</b><br>Provider-neutral instructions. Optional adapters for Claude Code and Codex.</p>

## what it does

Give Write Goal a rough task. It drafts one completion condition with four parts:

- the measurable result;
- actual evidence the assistant must surface;
- the user's constraints and approval gates;
- a stopping boundary that does not get confused with success.

The shared [skill instructions](skills/write-goal/SKILL.md) work as a reusable
prompt independently of an AI model or provider. Applications that load Agent
Skills can load the folder; other assistants can use the same instructions as
prompt context. Native installation is tested for Claude Code and Codex.

The [application adapters](skills/write-goal/references/hosts.md) choose syntax
from the destination application, rather than the model's name. A Claude model
in a plain API chat receives plain text. A native Claude Code goal receives a
`/goal` prefix. Codex receives plain completion text and uses actual goal tools
only when activation is explicitly requested and available.

## before and after

**Request:** "All 14 parser fixtures must pass. Do not modify production files.
Stop after 9 turns. The check is `python -m unittest discover -s tests/parser`."

**Plain draft — usable in either assistant:**

```text
All 14 parser fixtures pass, proven by actual `python -m unittest discover -s tests/parser` output showing every fixture passing with exit status 0. Do not modify production files. Do not weaken verification. Stop after 9 turns and report any unmet criteria without treating the stopping boundary as achievement.
```

For a native Claude Code goal, the adapter adds `/goal `. You can request plain
text in any application. If a check is unknown, the draft contains a visible
placeholder to replace before activation. A task with no concrete finish line
gets one clarifying question.

## install in Claude Code

In your terminal:

```bash
claude plugin install write-goal --marketplace edcadet10/write-goal
```

Start a new session and invoke `/write-goal:write-goal <rough task>`.
See [Claude's plugin installation guide](https://code.claude.com/docs/en/plugins/install).

## install in Codex

In your terminal:

```bash
codex plugin marketplace add edcadet10/write-goal
codex plugin add write-goal@write-goal
```

Start a new session and select the plugin's Write Goal skill. See
[OpenAI's plugin documentation](https://developers.openai.com/plugins/build/plugins).
The catalog is hosted in this GitHub repository and is separate from a public
plugin-directory listing. Native installation was tested with Claude Code
2.1.316 and Codex CLI 0.166.0.

## standalone skill

With Python 3.10+ and Git:

```bash
git clone https://github.com/edcadet10/write-goal.git
cd write-goal
python install.py --target claude
# Or:
python install.py --target codex
```

Use `python3` if that is your Python command. `./install.sh` forwards the same
options. No third-party Python packages are required.

| Destination | Standalone invocation | Default output |
| --- | --- | --- |
| Claude Code | `/write-goal <task>` | Native `/goal <condition>` line |
| Codex | `$write-goal <task>` | Plain completion condition |
| Other assistant | Supply the skill folder or paste its instructions as context | Plain completion condition |

Choose either plugin or standalone installation to avoid duplicate entries.
For manual installation without Python, download the standalone skill ZIP from
[Releases](https://github.com/edcadet10/write-goal/releases/latest) and keep the
entire `write-goal/` folder, including its adapter reference.

Claude's installer defaults to `~/.claude/skills/` and respects
`CLAUDE_CONFIG_DIR`. Codex defaults to `~/.agents/skills/`, or `$CODEX_HOME/skills/`
when set. Other applications use their own skill-loading paths. To choose a
skills parent directory explicitly:

```bash
python install.py --target codex --dest "/path with spaces/skills"
```

Identical reinstallations make no changes. Review local edits before replacing
a different installed copy with `--force`. The installer replaces this skill's
folder and leaves neighboring skills alone.

## drafting and activation

Drafting executes no task or verification command. It activates or replaces no
goal without an explicit request. Unknown applications acquire no assumed
slash commands, tool API, permissions, hooks, or scheduler. The skill does not
continue after a session ends or guarantee outcomes controlled by other people.

For native Claude Code `/goal`, workspace trust and permitted hooks are host
requirements. The evaluator uses evidence already surfaced in the conversation;
see the [official goal documentation](https://code.claude.com/docs/en/goal).
Codex and other applications retain their own capabilities and permissions.

## testing and contributing

```bash
python scripts/check.py
```

CI runs the portable suite on Windows, macOS, and Linux with Python 3.10 and
3.12. Real native installation checks use isolated host profiles and compare
the complete installed skill with source. Behavioral cases cover both native
adapters, a generic assistant, explicit plain text, and model/application
distinctions. See the [evaluation guide](evals/README.md) and
[contribution guide](CONTRIBUTING.md) for commands and evidence limitations.

Code and maintained source are hosted on GitHub. Report a reproducible issue
with fictional data through [GitHub issues](https://github.com/edcadet10/write-goal/issues).
See [SECURITY.md](SECURITY.md) for private vulnerability reporting.

## license

MIT. See [LICENSE](LICENSE).
