---
name: what-you-do-not-know
description: Constantly reminds the agent what it does NOT know, so it stops acting like an authority on things it has not researched or tool-verified. Use when installing/uninstalling the reminder hook, or when editing the list of "things not known" (topics.json).
---

# what-you-do-not-know

A tool that, on every user prompt and every tool call, injects a short reminder
of what the agent does **not** actually know — to stop it acting like an
authority on subjects it has not researched and claims it has not verified.

## The 4 stages of learning

1. **Unconscious incompetence** – You don't know what you don't know.
2. **Conscious incompetence** – You know what you don't know.
3. **Conscious competence** – You know, but using your knowledge requires a lot of concentration.
4. **Unconscious competence** – You know so well that you can use your knowledge instinctively.

The AI agent spends a lot of time at stage 1. If asked very directly and
insistently, it will agree to stage 2, then discover or search for answers and
reach stage 3. It genuinely has stage 4 for many *basic* things — but it acts as
if it has stage 4 for many *complex* things, which in reality puts it back to
stage 1 in practice.

**This skill's main goal is to elevate the base agent's awareness so that
stage 2 (you know what you don't know) is the baseline.** It does this with a
hook that injects a small string on every PreToolUse and UserPromptSubmit event.
The injected string is added to agent-visible context (same mechanism the
`source-of-truth-agent-tool` skill uses) and is also echoed to the user so they
can see it is being sent and see its current content.

## Files

| File | Purpose |
| --- | --- |
| `SKILL.md` | This file. |
| `topics.json` | The list of things the agent "knows" / "does not know". Edit this to change the message. |
| `inject_incompetence.py` | Engine-agnostic core: assembles and returns the prompt from `topics.json`. |
| `claude_adapter_inject_incompetence.py` | Claude-specific: reacts to Claude hooks, injects to agent context + echoes to user. |
| `claude_install.py` | Installs the hook into `~/.claude/settings.json`. |
| `claude_uninstall.py` | Uninstalls the hook. |

## Install / uninstall (Claude Code)

```
python3 claude_install.py      # register the hook on UserPromptSubmit + PreToolUse
python3 claude_uninstall.py    # remove it
```

Install is idempotent and backs up `settings.json` before changing it. Start a
new Claude Code session after installing for the hook to take effect.

## Updating the message

Edit `topics.json` — no reinstall needed; the hook reads it fresh each time.

- `preamble` — the opening line.
- `known_but_verify_note` — the stage-1-vs-stage-4 caution.
- `things_you_do_not_know` — the bullet list of items to treat as unknown until
  tool-verified.

Preview the assembled message with:

```
python3 inject_incompetence.py
```

## OpenCode support — BACKLOG

OpenCode-specific files (an OpenCode adapter + install/uninstall) are **not yet
implemented**. See `BACKLOG.md`. OpenCode's hook/extension shape may differ from
Claude's (it may not be hook-based), so the adapter layer will likely differ
while `inject_incompetence.py` and `topics.json` stay shared.
