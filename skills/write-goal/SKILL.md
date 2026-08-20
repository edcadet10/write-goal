---
name: write-goal
description: >-
  Turn a rough task into a ready-to-paste `/goal` completion condition for
  Claude Code's built-in /goal command. Use whenever the user wants to write,
  draft, or generate a goal prompt, or set up an autonomous "keep working until
  X is true" loop.
allowed-tools: Read Grep Glob AskUserQuestion
---

# Write a /goal condition

Generate ONE copy-paste-ready `/goal <condition>` line for Claude Code's
built-in **/goal** command.

Context you must respect: `/goal` keeps Claude working across turns until a
**small fast model (Haiku by default)** confirms the condition is met. That
evaluator **cannot run tools or read files** — it only judges what Claude has
already printed into the conversation. Every condition must therefore be
provable from Claude's own output.

## Step 1 — Get the task

The task is the text the user typed after `/write-goal` (`$ARGUMENTS`).

- Clarify only when the task omits the affected thing or its concrete desired
  state. Ask **exactly one** concise question: *"What concrete state should be
  true when this is finished?"* In that turn, print only that question and wait.
  Do not ask how to verify it or add examples, options, or follow-up questions.
- A task is concrete when it names the affected thing and the state it must
  reach; for example, "process every queued invoice exactly once with no
  duplicate charges" is concrete. A missing verification command does **not**
  make it vague. Generate the goal and mark an unknown check as
  `<verification command>` or `<verification query>` for the user to replace.
- Never invent a table, endpoint, script, or command and present it as real.
  Never copy a command from an example unless project inspection confirms it.
- Make reasonable assumptions for everything else. If a project is present and
  inspection is cheap, read `package.json`, `Makefile`, or test config
  (Read/Grep/Glob) and use the project's real commands.

## Step 2 — Build the condition

Write one condition in plain prose with these four ingredients:

1. **Measurable end state** — a concrete signal: a test result, a build/exit
   code, a file count, an empty queue, or a size budget. Ban fuzzy words such as
   "works", "clean", "good", and "done".
2. **Transcript-visible proof** — name the exact verified check whose output will
   land in the conversation. Examples include a verified `npm test` exiting 0,
   `npx tsc --noEmit` reporting no errors, or
   `gh issue list --label p0 --state open` returning an empty list. If no real
   check is known, use a visible placeholder. The proof must be something Claude
   prints, not something the evaluator inspects.
3. **Constraints** — what must NOT change on the way there, e.g. "do not modify
   files outside src/auth" or "do not weaken any test assertion".
4. **Turn cap** — end with a bound so it cannot loop forever, e.g. "If not
   satisfied within 30 turns, stop and summarize what remains." Default to 25–40
   turns sized to the task unless the user gave a number.

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

## Step 3 — Output

If Step 1 requires clarification, output only its one question. Otherwise print
the line in a copy-paste block:

```text
/goal <the condition you built>
```

After the block, print at most two short lines total:

1. The **first time** you generate a goal in a session, state that `/goal` runs
   only in a **trusted workspace** and is blocked if hooks are disabled.
2. Offer: *"Want it stricter, looser, or a different turn cap?"* Refine and
   reprint if the user reacts.

Do not restate or explain the goal or its placeholders outside the block.

## Examples

These commands are valid only because each example states the context that
provides them. Do not reuse them without that context.

**Task:** migrate the auth module to the new API

**Known context:** project commands are unavailable.

```text
/goal Every call site under src/auth uses the new client API, proven in the transcript by `<auth test command>` and `<typecheck command>` both exiting 0. Do not modify files outside src/auth or weaken any test assertion. If not satisfied within 30 turns, stop and list the remaining call sites.
```

**Task:** utils.js is too big, split it

**Known context:** the inspected project defines `npm run build` and `npm test`.

```text
/goal src/utils.js is split into focused modules each under 200 lines with all imports updated, proven in the transcript by `npm run build` and `npm test` both exiting 0 with the same passing-test count as before. Do not change any exported function signature. Stop after 25 turns and report what remains.
```

**Task:** process every invoice currently in the queue exactly once, with no
duplicate charges

**Known context:** no verification interface was supplied.

```text
/goal Every invoice that was in the queue at the start is marked processed exactly once and no charge identifier occurs more than once, proven in the transcript by `<verification query>` reporting zero initially queued invoices unprocessed and zero duplicate charge identifiers. Do not process invoices added after the initial snapshot or retry a completed charge. Stop after 30 turns and report any invoice that remains.
```
