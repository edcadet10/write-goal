<p align="center">
  <img src="assets/banner.svg" alt="write-goal — turn a vague task into a /goal Claude can prove. A Claude Code skill." width="100%">
</p>

<p align="center">
  <a href="https://github.com/edcadet10/write-goal/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/edcadet10/write-goal/ci.yml?branch=main&amp;style=flat-square&amp;label=CI" alt="CI status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-4ecca3?style=flat-square" alt="MIT license"></a>
  <a href="https://code.claude.com/docs/en/skills"><img src="https://img.shields.io/badge/Claude%20Code-skill-7c5cff?style=flat-square&logo=anthropic&logoColor=white" alt="Claude Code skill"></a>
  <img src="https://img.shields.io/badge/pairs%20with-%2Fgoal-5eead4?style=flat-square" alt="Pairs with /goal">
  <img src="https://img.shields.io/badge/output-one%20provable%20%2Fgoal%20line-f5b14e?style=flat-square" alt="Output: one provable /goal line">
  <a href="CONTRIBUTING.md"><img src="https://img.shields.io/badge/contributions-welcome-22d3ee?style=flat-square" alt="Contributions welcome"></a>
</p>

<p align="center"><b>Hand it a rough task. Get back one <code>/goal</code> line that Claude can actually prove it finished.</b></p>

---

## how it came to life

I was poking at Claude Code's `/goal` command, trying to work out its switches, and somewhere in there it clicked that I'd been ignoring a whole built-in loop. `/goal <condition>` keeps Claude working across turns until the condition is true. I'd been babysitting long tasks by hand the entire time.

Then I hit the catch. A small fast model (Haiku, by default) is the one deciding when you're done, and it can't run commands or open files. It only sees what Claude has already printed into the chat. So "loop until the tests pass" is worthless if Claude never prints the test output, and "until the code is clean" never terminates because nothing makes "clean" true or false. A good goal has to carry its own proof.

I didn't want to solve that puzzle by hand every time I started a loop. So I asked for a skill that writes the goal for me: give it a rough task, hand me back one line I can paste. That's `write-goal`. Funny enough, every task in the session where it was born was itself set with `/goal` — including the one that built this.

It's the second skill in my Claude Code arsenal, after [disconfirm](https://github.com/edcadet10/disconfirm).

## what it does

You run it with a rough task:

```text
/write-goal migrate the auth module to the new API
```

It hands back one `/goal` line with four things built in:

- a measurable end state, a real signal like an exit code or a file count, never "works" or "done"
- a proof that shows up in the transcript, a specific command whose output Claude prints
- the constraints to hold, what must not change on the way there
- a turn cap, so a stuck loop stops and reports instead of running forever

If your task is too vague to have a finish line, it asks you exactly one question and then gets on with it. One question, never a quiz.

## how it builds the goal

```mermaid
flowchart LR
    T(["rough task"]) --> M["measurable<br/>end state"]
    T --> P["transcript-visible<br/>proof"]
    T --> C["constraints"]
    T --> K["turn cap"]
    M --> G(["one /goal line<br/>Claude can prove"])
    P --> G
    C --> G
    K --> G

    classDef task fill:#f5b14e,stroke:#ffd596,color:#1a1206
    classDef part fill:#0b0e14,stroke:#4ecca3,color:#cfeee2
    classDef out fill:#0f2a22,stroke:#4ecca3,color:#9ff0d2
    class T task
    class M,P,C,K part
    class G out
```

## install

From the repo root:

```bash
./install.sh
```

It drops the skill into `~/.claude/skills/` and tells you how to call it. Or do it by hand:

```bash
cp -r skills/write-goal ~/.claude/skills/
```

No hook, no settings to edit. It runs when you call `/write-goal`, and not a moment otherwise.

## a real example

Rough task in:

```text
/write-goal utils.js is too big, split it
```

`/goal` line out:

```text
/goal src/utils.js is split into focused modules each under 200 lines with all imports updated, proven in the transcript by `npm run build` and `npm test` both exiting 0 with the same passing-test count as before. Do not change any exported function signature. Stop after 25 turns and report what remains.
```

Read it back and you can see the four ingredients: the end state (modules under 200 lines, imports updated), the proof Claude has to print (`build` and `test` both exit 0, test count unchanged), the constraint (no signature changes), and the cap (25 turns, then report).

## the one rule it never breaks

The proof has to be something Claude prints, not something the evaluator goes and checks. That single fact is what makes goals terminate instead of spinning. Every line the skill writes is built around it.

## contribute

Contributions are welcome. Read the [guide](CONTRIBUTING.md), open an [issue](https://github.com/edcadet10/write-goal/issues/new/choose), or discuss broad changes in [Discussions](https://github.com/edcadet10/write-goal/discussions). Run `./scripts/check.sh` before opening a PR.

## part of my arsenal

One of the skills I lean on daily in Claude Code, published so other people can use it too. If it saves you from one loop that ran twelve turns past done because the goal couldn't tell it was finished, it earned its place.

## license

MIT. Fork it, tighten it, make it yours. See [LICENSE](LICENSE).
