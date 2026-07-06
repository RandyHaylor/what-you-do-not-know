#!/usr/bin/env python3
"""Assemble the "what you do not know" reminder from topics.json.

Cross-platform (no OS-specific calls). This is the engine-agnostic core and the
ONLY script that reads topics.json. Host adapters (e.g.
claude_adapter_inject_incompetence.py) call build_reminder_payload() and wrap
the returned values in whatever shape their host expects.

build_reminder_payload() returns a dict with the agent message and the user
message kept SEPARATE, plus a per-hook-event trigger flag for each event this
skill can react to:

    {
      "trigger_on_tool_use": true,           # settings.trigger_on_tool_use
      "trigger_on_user_prompt_submit": true, # settings.trigger_on_user_prompt_submit
      "agent_message": "<full text>",        # always the full reminder, for agent context
      "user_message": "<text>"               # per settings.user_echo_detail
    }

User-echo detail levels (settings.user_echo_detail):
  - "full"    : preamble + "What you don't know:" + every bullet (default).
  - "compact" : only the bullets.
  - "minimal" : one line, e.g. "...reminded agent it knows 3 things it does
                not know...".

The two trigger flags replace a single active/passive mode: each hook event
(PreToolUse, UserPromptSubmit) is switched on/off independently. Setting both
to false means no hook injection at all -- only the SKILL.md manifest stands.
The host adapter picks the flag matching the event it was invoked for and
emits nothing when that flag is false.

Run directly to print the payload as JSON to stdout (preview):

    python3 inject_incompetence.py
"""
import json
import os
import sys

TOPICS_JSON_FILENAME = "topics.json"

USER_ECHO_DETAIL_FULL = "full"
USER_ECHO_DETAIL_COMPACT = "compact"
USER_ECHO_DETAIL_MINIMAL = "minimal"

DEFAULT_TRIGGER_ON_TOOL_USE = True
DEFAULT_TRIGGER_ON_USER_PROMPT_SUBMIT = True
DEFAULT_USER_ECHO_DETAIL = USER_ECHO_DETAIL_FULL

WHAT_YOU_DONT_KNOW_HEADER = "What you don't know:"


def path_to_topics_json():
    """Absolute path to topics.json sitting next to this script."""
    script_directory_absolute_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory_absolute_path, TOPICS_JSON_FILENAME)


def load_topics_config():
    """Read and parse topics.json. Returns the parsed dict."""
    with open(path_to_topics_json(), "r", encoding="utf-8") as topics_file:
        return json.load(topics_file)


def _bullet_lines(things_you_do_not_know):
    """Render each 'not known' item as an indented bullet line."""
    return [f"  - {item}" for item in things_you_do_not_know]


def build_full_message(preamble, things_you_do_not_know):
    """Full reminder: preamble + header + every bullet. Used for the agent
    message always, and for the 'full' user-echo detail level."""
    lines = []
    if preamble:
        lines.append(preamble)
    lines.append(WHAT_YOU_DONT_KNOW_HEADER)
    lines.extend(_bullet_lines(things_you_do_not_know))
    return "\n".join(lines)


def build_compact_message(things_you_do_not_know):
    """Compact user echo: only the bullets, no preamble or header."""
    return "\n".join(_bullet_lines(things_you_do_not_know))


def build_minimal_message(things_you_do_not_know):
    """Minimal user echo: a single summary line with the item count."""
    item_count = len(things_you_do_not_know)
    return f"...reminded agent it knows {item_count} things it does not know..."


def build_user_message(user_echo_detail, preamble, things_you_do_not_know):
    """Pick the user-echo string for the configured detail level. Unknown
    values fall back to the full message."""
    if user_echo_detail == USER_ECHO_DETAIL_MINIMAL:
        return build_minimal_message(things_you_do_not_know)
    if user_echo_detail == USER_ECHO_DETAIL_COMPACT:
        return build_compact_message(things_you_do_not_know)
    return build_full_message(preamble, things_you_do_not_know)


def build_reminder_payload(topics_config=None):
    """Assemble the reminder payload from topics.json.

    Returns {"trigger_on_tool_use": bool, "trigger_on_user_prompt_submit": bool,
    "agent_message": str, "user_message": str}.
    """
    if topics_config is None:
        topics_config = load_topics_config()

    settings = topics_config.get("settings", {})
    trigger_on_tool_use = settings.get("trigger_on_tool_use", DEFAULT_TRIGGER_ON_TOOL_USE)
    trigger_on_user_prompt_submit = settings.get(
        "trigger_on_user_prompt_submit", DEFAULT_TRIGGER_ON_USER_PROMPT_SUBMIT
    )
    user_echo_detail = settings.get("user_echo_detail", DEFAULT_USER_ECHO_DETAIL)

    preamble = topics_config.get("preamble", "").strip()
    things_you_do_not_know = topics_config.get("things_you_do_not_know", [])

    agent_message = build_full_message(preamble, things_you_do_not_know)
    user_message = build_user_message(user_echo_detail, preamble, things_you_do_not_know)

    return {
        "trigger_on_tool_use": bool(trigger_on_tool_use),
        "trigger_on_user_prompt_submit": bool(trigger_on_user_prompt_submit),
        "agent_message": agent_message,
        "user_message": user_message,
    }


def _main():
    try:
        payload = build_reminder_payload()
    except FileNotFoundError:
        print(f"ERROR: {TOPICS_JSON_FILENAME} not found next to inject_incompetence.py",
              file=sys.stderr)
        return 1
    except json.JSONDecodeError as parse_error:
        print(f"ERROR: {TOPICS_JSON_FILENAME} is not valid JSON: {parse_error}",
              file=sys.stderr)
        return 1
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
