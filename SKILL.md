---
name: what-you-do-not-know
description: >-
  Keeps the agent at stage 2 of learning — "you know what you don't know" —
  instead of acting like an authority on things it has not researched or
  tool-verified. The 4 stages of learning: (1) unconscious incompetence — you
  don't know what you don't know; (2) conscious incompetence — you know what you
  don't know; (3) conscious competence — you know but it takes concentration;
  (4) unconscious competence — you know instinctively. The agent genuinely has
  stage 4 only for basic things, yet often acts as if it has stage 4 for complex
  things, which is really stage 1. Before each response or task, act according to
  knowing what you don't know, and treat these as things you do NOT or CANNOT
  know for certain without tool verification: the first thing you suspect to be
  the problem is actually the problem without concrete proof; the best current
  solution to a design or troubleshooting problem without a real web search
  first; that you know better than the user about any given topic. Also use this
  skill when installing/uninstalling the reminder hook, editing the list of
  "things not known", or changing settings in topics.json.
---

# what-you-do-not-know

A tool that injects a short reminder of what the agent does **not** actually
know — on every user prompt and/or every tool call, independently configurable
(see Settings) — to stop it acting like an authority on subjects it has not
researched and claims it has not verified.

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
hook that injects a small string on the PreToolUse and/or UserPromptSubmit
event, independently switchable per event (see Settings below). The injected
string is added to agent-visible context (same mechanism the
`source-of-truth-agent-tool` skill uses) and the user echo is shown to the user
so they can see it is being sent and see its current content. With both
triggers off, there is no hook injection at all — only this SKILL.md manifest
(the frontmatter `description`, loaded into every session) stands as the
impetus to act according to the stages of learning.

## Files

| File | Purpose |
| --- | --- |
| `SKILL.md` | This file. Its frontmatter `description` is the manifest injected into every session — it carries the stages of learning and the "things not known" so the reminder still stands even with both hook triggers off. |
| `topics.json` | Settings + the list of things the agent "knows" / "does not know". Edit this to change the message. |
| `inject_incompetence.py` | Engine-agnostic core; the ONLY script that reads `topics.json`. Returns a JSON payload with the agent message and user message separate, plus a per-event trigger flag. |
| `claude_adapter_inject_incompetence.py` | Claude-specific: reacts to Claude hooks, injects the agent message to agent context + echoes the user message to the user. Emits nothing for an event whose trigger flag is off. |
| `claude_install.py` | Installs the hook into `~/.claude/settings.json`. |
| `claude_uninstall.py` | Uninstalls the hook. |

## Install / uninstall (Claude Code)

```
python3 claude_install.py      # register the hook on UserPromptSubmit + PreToolUse
python3 claude_uninstall.py    # remove it
```

Install is idempotent and backs up `settings.json` before changing it. Start a
new Claude Code session after installing for the hook to take effect.

## Settings (`topics.json` → `settings`)

| Setting | Values | Shipped default | Meaning |
| --- | --- | --- | --- |
| `trigger_on_tool_use` | `true` / `false` | `false` | Whether the hook injects on `PreToolUse` (every tool call). |
| `trigger_on_user_prompt_submit` | `true` / `false` | `true` | Whether the hook injects on `UserPromptSubmit` (every user prompt). |
| `user_echo_detail` | `full` / `compact` / `minimal` | `minimal` | How much of the reminder the USER sees. The AGENT always receives the full message. |

"Shipped default" is what's in `topics.json` as committed. If a setting key is
missing from `topics.json` entirely (not just a fresh install — an edited file
that dropped a key), the code falls back to `true` / `true` / `full`
respectively — this is a robustness fallback, not the shipped behavior.

Setting both `trigger_on_tool_use` and `trigger_on_user_prompt_submit` to
`false` is the passive equivalent: no hook injection at all, only the SKILL.md
manifest stands.

`user_echo_detail` levels:

- `full` — preamble + `What you know you don't know includes:` + every bullet.
- `compact` — only the bullets.
- `minimal` — one line, e.g. `...reminded agent it knows 3 things it does not know...`.

## Updating the message

Edit `topics.json` — no reinstall needed; the hook reads it fresh each time.

- `settings` — see the table above.
- `preamble` — the opening line.
- `things_you_do_not_know` — the bullet list of items to treat as unknown until
  tool-verified.

Preview the assembled payload (agent + user messages, and both trigger flags) with:

```
python3 inject_incompetence.py
```

## OpenCode support — BACKLOG

OpenCode-specific files (an OpenCode adapter + install/uninstall) are **not yet
implemented**. See `BACKLOG.md`. OpenCode's hook/extension shape may differ from
Claude's (it may not be hook-based), so the adapter layer will likely differ
while `inject_incompetence.py` and `topics.json` stay shared.
