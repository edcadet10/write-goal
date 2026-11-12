# Optional application adapters

No listed application is required for the plain-text workflow. Use the shared
instructions with your chosen assistant and select an adapter only for a known
destination interface.

These adapters change presentation and activation, not the shared completion
criteria. Choose the destination application from the request or environment.
A model's name does not identify the application. Explicit plain-text output
always keeps the shared condition without an application prefix.

## Claude Code

For a native Claude Code goal line, prepend the literal `/goal ` to the completed
condition and verify it starts the line. A note about Claude Code outside the
block does not replace this prefix. Keep the condition below its 4,000-character
limit. The first time in a session, note that native `/goal` requires workspace
trust and permitted hooks. These requirements concern activation, not drafting.

Claude Code's completion evaluator judges evidence already surfaced in the
conversation; it cannot independently run checks or open project files. Return
the draft for the user to invoke unless activation was explicitly requested and
a real activation mechanism is available. Do not claim printing a code block
activated the command.

## Codex

Keep the condition as plain text without an invented slash command. When
activation is explicitly requested and native goal tools are available, use
the actual tools and report the result. Preserve an existing active goal unless
replacement was explicitly authorized. If activation is unavailable, return the
draft and say so. Do not apply another application's trust or hook requirements.

## Other assistants and applications

Use the same plain completion text. Add native syntax only if the destination's
actual interface is known. Do not assume a scheduler, evaluator, tool API, or
permission system. The instructions work as a reusable prompt even when the
application has no Agent Skills loader or persistent-goal feature.
