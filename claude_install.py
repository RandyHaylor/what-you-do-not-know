#!/usr/bin/env python3
"""Install the "what you do not know" hook into ~/.claude/settings.json.

Cross-platform. Idempotently registers the Claude adapter on two hook events:

  - UserPromptSubmit : reminds the agent on every user prompt.
  - PreToolUse       : reminds the agent before every tool call.

Both entries run claude_adapter_inject_incompetence.py, which injects the
reminder into agent-visible context and echoes it to the user.

Safe to run repeatedly: existing entries pointing at this skill directory are
detected and left alone; a timestamped backup of settings.json is written
before any modification.

    python3 claude_install.py
"""
import datetime
import json
import os
import shutil
import sys

SKILL_DIRECTORY_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
CLAUDE_ADAPTER_FILENAME = "claude_adapter_inject_incompetence.py"
HOOK_EVENT_NAMES_TO_REGISTER = ("UserPromptSubmit", "PreToolUse")
HOOK_MATCHER = "*"


def path_to_claude_settings_json():
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def python_launcher_command():
    """Command used to launch python in the hook, quoted for the current OS."""
    return f'"{sys.executable}"'


def hook_command_string():
    adapter_path = os.path.join(SKILL_DIRECTORY_ABSOLUTE_PATH, CLAUDE_ADAPTER_FILENAME)
    return f'{python_launcher_command()} "{adapter_path}"'


def load_or_init_settings(settings_path):
    if os.path.isfile(settings_path):
        with open(settings_path, "r", encoding="utf-8") as settings_file:
            return json.load(settings_file)
    return {}


def backup_settings_file(settings_path):
    if not os.path.isfile(settings_path):
        return None
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_path = f"{settings_path}.bak.{timestamp}"
    shutil.copyfile(settings_path, backup_path)
    return backup_path


def entry_already_points_at_this_skill(settings_data, hook_event_name):
    """True if an entry for this event already runs this skill's adapter."""
    for entry in settings_data.get("hooks", {}).get(hook_event_name, []):
        for hook in entry.get("hooks", []):
            command = hook.get("command", "")
            if SKILL_DIRECTORY_ABSOLUTE_PATH in command and CLAUDE_ADAPTER_FILENAME in command:
                return True
    return False


def append_hook_entry(settings_data, hook_event_name, command):
    hooks_root = settings_data.setdefault("hooks", {})
    event_list = hooks_root.setdefault(hook_event_name, [])
    event_list.append({
        "matcher": HOOK_MATCHER,
        "hooks": [{"type": "command", "command": command}],
    })


def write_settings(settings_path, settings_data):
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    with open(settings_path, "w", encoding="utf-8") as settings_file:
        json.dump(settings_data, settings_file, indent=2)
        settings_file.write("\n")


def _main():
    settings_path = path_to_claude_settings_json()
    settings_data = load_or_init_settings(settings_path)
    command = hook_command_string()

    settings_was_modified = False
    for hook_event_name in HOOK_EVENT_NAMES_TO_REGISTER:
        if entry_already_points_at_this_skill(settings_data, hook_event_name):
            print(f"  {hook_event_name}: already registered -- no change")
            continue
        append_hook_entry(settings_data, hook_event_name, command)
        settings_was_modified = True
        print(f"  {hook_event_name}: registered -> {command}")

    if not settings_was_modified:
        print("Nothing to do; hook already installed.")
        return 0

    backup_path = backup_settings_file(settings_path)
    if backup_path:
        print(f"  backed up settings -> {backup_path}")
    write_settings(settings_path, settings_data)
    print(f"Installed. Wrote {settings_path}")
    print("Restart or start a new Claude Code session for the hook to take effect.")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
