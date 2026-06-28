---
name: write-goal
description: Turn a rough task into a ready-to-paste `/goal <condition>` line for Claude Code's built-in /goal command. Use whenever the user wants to write, draft, or generate a goal prompt, or set up an autonomous "keep working until X is true" loop.
allowed-tools: Read, Grep, Glob, AskUserQuestion
---

# Write a /goal condition

Generate ONE copy-paste-ready `/goal <condition>` line for Claude Code's built-in **/goal** command.

Context you must respect: `/goal` keeps Claude working across turns until a **small fast model (Haiku by default)** confirms the condition is met. That evaluator **cannot run tools or read files** — it only judges what Claude has already printed into the conversation. So every condition must be provable from Claude's own output.

## Step 1 — Get the task
The task is the text the user typed after `/write-goal` (`$ARGUMENTS`).
- If it's empty or too vague to have a verifiable end state, ask **exactly one** concise question: *"What's the finish line — what should be true when this is done, and how would Claude prove it (a command, a file, a count)?"* Then proceed.
- Never ask more than one question. Make reasonable assumptions for everything else.
- If a project is present and it's cheap, peek at `package.json` / `Makefile` / test config (Read/Grep/Glob) to use the project's REAL commands in the proof. Otherwise use a sensible command and flag it as a placeholder to adjust.

## Step 2 — Build the condition
Write one condition in plain prose with these four ingredients:

1. **Measurable end state** — a concrete signal: a test result, a build/exit code, a file count, an empty queue, a size budget. Ban fuzzy words like "works", "clean", "good", "done".
2. **Transcript-visible proof** — name the exact check whose output will land in the conversation, e.g. `` `npm test` exits 0 ``, `` `npx tsc --noEmit` reports no errors ``, `` `gh issue list --label p0 --state open` returns an empty list ``. The proof must be something Claude prints, not something the evaluator inspects.
3. **Constraints** — what must NOT change on the way there, e.g. "do not modify files outside src/auth", "do not weaken any test assertion".
4. **Turn cap** — end with a bound so it can't loop forever, e.g. "If not satisfied within 30 turns, stop and summarize what remains." Default to 25–40 turns sized to the task unless the user gave a number.

## Hard rules
- Output stays **under 4,000 characters** (the /goal limit).
- Produce **exactly one** condition (one goal per session).
- The proof must be demonstrable from Claude's own output — never "the evaluator checks the file".

## Step 3 — Output
Print the line in a copy-paste block, then at most two short lines: what the proof is, and any placeholder to adjust. Keep it scannable.

```text
/goal <the condition you built>
```

Then offer: *"Want it stricter, looser, or a different turn cap?"* — and refine + reprint if they react.

The **first time** you generate a goal in a session, add one reminder: `/goal` runs only in a **trusted workspace** (and is blocked if hooks are disabled).

## Examples

**Task:** migrate the auth module to the new API
```text
/goal Every call site under src/auth uses the new client API, proven in the transcript by `npm test -- test/auth` exiting 0 and `npx tsc --noEmit` reporting no errors. Do not modify files outside src/auth or weaken any test assertion. If not satisfied within 30 turns, stop and list the remaining call sites.
```

**Task:** utils.js is too big, split it
```text
/goal src/utils.js is split into focused modules each under 200 lines with all imports updated, proven in the transcript by `npm run build` and `npm test` both exiting 0 with the same passing-test count as before. Do not change any exported function signature. Stop after 25 turns and report what remains.
```

**Task:** clear the p0 bug backlog
```text
/goal Every issue labeled p0 is closed, proven in the transcript by `gh issue list --label p0 --state open` returning an empty list, with each fix in its own commit. Do not close an issue without a corresponding code change. Stop after 40 turns and report any issue left open and why.
```
