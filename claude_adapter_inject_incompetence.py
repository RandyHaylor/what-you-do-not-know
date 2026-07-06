#!/usr/bin/env python3
"""Claude Code hook adapter for the "what you do not know" skill.

This is the layer that reacts to Claude Code hooks. It is invoked by both the
UserPromptSubmit and PreToolUse hook entries (see claude_install.py). It:

  1. Builds the reminder payload from topics.json (via inject_incompetence),
     which returns the agent message and user message separately, plus a
     trigger flag for each hook event this skill reacts to
     (trigger_on_tool_use, trigger_on_user_prompt_submit).
  2. Picks the flag matching the event that actually fired. If it is false,
     emits nothing (no hook injection) for that event; only the SKILL.md
     manifest stands. Setting both flags false is the passive equivalent.
  3. Otherwise emits the AGENT message to Claude via the hook JSON contract
     `hookSpecificOutput.additionalContext` -- the same mechanism the
     source-of-truth-agent-tool skill uses to reach agent-visible context.
     NOTE: additionalContext is injected silently; the USER does not see it.
  4. Echoes the USER message (whose verbosity follows settings.user_echo_detail)
     to the user via the top-level `systemMessage` JSON field ("Warning shown to
     user" per the Claude Code hooks docs). This is the supported way to surface
     text to the user on a non-blocking (exit 0) run. Hook stderr on exit 0 is
     dropped by Claude Code, so stderr is NOT used for the user echo.

Fails silently (emits empty JSON, exit 0) on any error so a broken skill never
blocks the user's tool calls or prompts.

Reads the hook payload as JSON on stdin; the only field it needs is
`hook_event_name` so it can stamp the correct event name in its response.
"""
import json
import os
import sys

SCRIPT_DIRECTORY_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))

# Hook events this adapter knows how to answer, mapped to the topics.json
# settings key that switches injection on/off for that event.
HOOK_EVENT_NAME_TO_TRIGGER_SETTING_KEY = {
    "UserPromptSubmit": "trigger_on_user_prompt_submit",
    "PreToolUse": "trigger_on_tool_use",
}
DEFAULT_HOOK_EVENT_NAME = "UserPromptSubmit"


def _emit_empty_and_exit_silently():
    """Emit a no-op response so the host proceeds unaffected."""
    print("{}")
    sys.exit(0)


def _read_hook_event_name_from_stdin():
    """Parse the hook payload from stdin and return its hook_event_name.

    Accepts both snake_case (`hook_event_name`) and camelCase (`hookEventName`)
    since Claude Code has used both across versions. Falls back to the default.
    """
    try:
        raw_stdin = sys.stdin.read()
        if not raw_stdin.strip():
            return DEFAULT_HOOK_EVENT_NAME
        payload = json.loads(raw_stdin)
    except Exception:
        return DEFAULT_HOOK_EVENT_NAME

    event_name = payload.get("hook_event_name") or payload.get("hookEventName")
    if event_name in HOOK_EVENT_NAME_TO_TRIGGER_SETTING_KEY:
        return event_name
    return DEFAULT_HOOK_EVENT_NAME


def _main():
    sys.path.insert(0, SCRIPT_DIRECTORY_ABSOLUTE_PATH)
    try:
        from inject_incompetence import build_reminder_payload
    except Exception:
        _emit_empty_and_exit_silently()
        return

    hook_event_name = _read_hook_event_name_from_stdin()

    try:
        reminder_payload = build_reminder_payload()
    except Exception:
        _emit_empty_and_exit_silently()
        return

    # Skip injection if the flag for THIS event is off -- the SKILL.md manifest
    # still stands regardless. Setting both flags false is the passive equivalent.
    trigger_setting_key = HOOK_EVENT_NAME_TO_TRIGGER_SETTING_KEY[hook_event_name]
    if not reminder_payload.get(trigger_setting_key, True):
        _emit_empty_and_exit_silently()
        return

    agent_message = reminder_payload.get("agent_message", "")
    user_message = reminder_payload.get("user_message", "")
    user_facing_echo = f"[what-you-do-not-know] reminder injected:\n{user_message}"

    # systemMessage  -> shown to the USER (non-blocking, exit 0).
    # additionalContext -> injected into the AGENT's context (not user-visible).
    print(json.dumps({
        "systemMessage": user_facing_echo,
        "hookSpecificOutput": {
            "hookEventName": hook_event_name,
            "additionalContext": agent_message,
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    try:
        _main()
    except Exception:
        _emit_empty_and_exit_silently()
