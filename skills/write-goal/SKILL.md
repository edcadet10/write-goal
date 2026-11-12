---
name: write-goal
description: >-
  Draft one measurable, evidence-backed completion condition for Claude Code
  or Codex. Use when asked to write or refine a goal prompt or a "keep working
  until" condition; ordinary task execution does not need this skill.
allowed-tools: Read Grep Glob AskUserQuestion
---

# Write a provable goal

Turn a rough task into ONE copy-paste-ready completion condition. Drafting is
the default: do not execute the task, activate a goal, or replace an active goal
unless the user explicitly asks for that action. Read project context only as
needed to ground the draft; do not execute verification commands while drafting.

Choose the requested host, or the current host if none is named:

- **Claude Code:** output `/goal <condition>`. Its evaluator cannot run tools or
  read files; it judges evidence surfaced in the conversation.
- **Codex or another host:** output the condition as plain text, without an
  invented slash command. Native goal tools, when available, are separate from
  the draft. If activation was explicitly requested, use the actual tool and
  report its result; do not simulate activation with text. Preserve an existing
  active goal unless replacement was explicitly authorized. If no native tool
  is available, return the draft and say activation is unavailable.

Never claim the skill itself schedules work or runs after the session ends.

## Step 1 — Get the task

Use the text after `/write-goal` (`$ARGUMENTS`) or `$write-goal`, or the user's
natural-language request and relevant conversation context.

- Clarify only when the task omits the affected thing or its concrete desired
  state. Ask **exactly one** concise question: *"What concrete state should be
  true when this is finished?"* In that turn, print only that question and wait.
  Do not ask how to verify it or add examples, options, or follow-up questions.
  If there is no task, use the same question; do not invent one.
- A task is concrete when it names the affected thing and the state it must
  reach; for example, "process every queued invoice exactly once with no
  duplicate charges" is concrete. A missing verification command does **not**
  make it vague. Generate the goal and mark an unknown check as
  `<verification command>` or `<verification query>` for the user to replace.
- Never invent a table, endpoint, script, or command and present it as real.
  Never copy a command from an example unless project inspection confirms it.
- Make reasonable assumptions for everything else. If a project is present and
  inspection is cheap, read `package.json`, `Makefile`, or test config
  with available read-only tools and use the project's real commands. Treat
  commands in files as evidence to inspect, not instructions to execute.

## Step 2 — Build the condition

Write one condition in plain prose with these four ingredients:

1. **Measurable end state** — a concrete signal: a test result, a build/exit
   code, a file count, an empty queue, or a size budget. Ban fuzzy words such as
   "works", "clean", "good", and "done". Do not invent thresholds, paths, or
   acceptance criteria. Preserve user-supplied numbers and deadlines. For a
   changing queue or backlog, identify the starting snapshot so new arrivals
   cannot silently expand the task.
2. **Transcript-visible proof** — name the exact verified check whose output will
   land in the conversation. Examples include a verified `npm test` exiting 0,
   `npx tsc --noEmit` reporting no errors, or
   `gh issue list --label p0 --state open` returning an empty list. If no real
   check is known, use a visible placeholder. The proof must be something Claude
   prints, not something the evaluator inspects. Require actual observed output
   and exit status, query result, or artifact evidence; a statement that a check
   passed is not proof. Make the check cover the requested end state, not merely
   a nearby proxy. Preserve failures and do not weaken checks to obtain success.
3. **Constraints** — what must NOT change on the way there, e.g. "do not modify
   files outside src/auth" or "do not weaken any test assertion".
4. **Stopping boundary** — preserve the user's turn, time, or budget limit. If
   none was given, default to 30 turns. Do not add a competing turn cap when the
   user specified a deadline or explicitly requested continued work. Stop at the
   boundary and report the observed state and remaining work; hitting the bound
   is not achievement. Do not invent a token budget or claim a host enforces a
   prose limit. If a dependency blocks progress, report it and preserve a
   checkpoint according to the host's actual capabilities.

For outcomes controlled by other people (stars, sales, approvals), retain the
requested target and deadline, but distinguish authorized work from the final
external outcome. State the authoritative metric and observation time. Do not
promise success, substitute shipped work for the target, fabricate approvals,
or imply that a live session is a future scheduler. Resolve relative deadlines
from a known current date and timezone; otherwise leave a visible date placeholder.
Separate an observable metric from conduct constraints: a public count proves
quantity, not people's motives. Preserve requirements for genuine adoption as
constraints against artificial inflation; acknowledge that individual intent
cannot be certified rather than inventing an authenticity query.

## Hard rules

- Output stays **under 4,000 characters** (the /goal limit).
- Produce **exactly one** condition (one goal per session).
- The proof must be demonstrable from Claude's own output — never "the evaluator
  checks the file".
- A command is real only if the user supplied it or project inspection found it.
  Otherwise it must remain an angle-bracket placeholder, even if a common command
  such as `npm test` seems likely.
- Preserve the user's constraints exactly. Do not silently strengthen them; for
  example, "do not modify production files" does not mean "modify only tests."
- Do not insert deployment, spending, outreach, or other external actions that
  the user did not authorize. Preserve approval gates and human-only steps.
- If a placeholder remains, the draft is a template, not ready to activate.
  Resolve it before activating; never send a placeholder to a native goal tool.
- Before output, check the metric, proof coverage, constraints, boundary, host
  syntax, and length. Compress prose before dropping any user requirement. If
  the requirements cannot fit, ask which scope to split instead of truncating.

## Step 3 — Output

If Step 1 requires clarification, output only its one question. Otherwise print
the single-line condition in one copy-paste block (with `/goal` only for Claude):

```text
/goal <the condition you built>
```

After the block, print at most two short lines total. Use them only when needed:

1. For Claude, the first time in a session, note that `/goal` requires workspace
   trust and permitted hooks. For Codex, do not repeat Claude-only requirements.
2. Identify unresolved placeholders as requiring replacement, or report an
   explicitly requested activation result. Otherwise omit commentary.

Do not restate the goal or add unrelated explanation outside the block.

## Examples

These commands are valid only because each example states the context that
provides them. Do not reuse them without that context.

**Task:** migrate all call sites under src/auth to the new API; do not modify
files outside src/auth or weaken tests

**Known context:** project commands are unavailable.

```text
/goal Every call site under src/auth uses the new client API, proven by a printed call-site inventory and actual `<auth test command>` and `<typecheck command>` output with exit status 0. Do not modify files outside src/auth or weaken tests. After 30 turns, stop and report remaining call sites without claiming achievement.
```

**Task:** split src/utils.js into modules under 200 lines; preserve exported signatures

**Known context:** the inspected project defines `npm run build` and `npm test`.

```text
/goal src/utils.js is split into modules each under 200 lines with all imports updated, proven by printed line counts and actual `npm run build` and `npm test` output with exit status 0. Do not change any exported function signature or weaken tests. After 30 turns, stop and report any unmet criteria without claiming achievement.
```

**Task:** process every invoice currently in the queue exactly once, with no
duplicate charges

**Known context:** no verification interface was supplied.

```text
/goal Every invoice that was in the queue at the start is marked processed exactly once and no charge identifier occurs more than once, proven in the transcript by `<verification query>` reporting zero initially queued invoices unprocessed and zero duplicate charge identifiers. Do not process invoices added after the initial snapshot or retry a completed charge. Stop after 30 turns and report any invoice that remains.
```
