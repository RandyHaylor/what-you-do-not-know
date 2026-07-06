#!/usr/bin/env python3
"""Uninstall the "what you do not know" hook from ~/.claude/settings.json.

Cross-platform. Removes every hook entry (on any event) whose command runs
this skill's Claude adapter, then prunes any now-empty event lists. Writes a
timestamped backup of settings.json before modifying it. Safe to run when
nothing is installed.

    python3 claude_uninstall.py
"""
import datetime
import json
import os
import shutil
import sys

SKILL_DIRECTORY_ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
CLAUDE_ADAPTER_FILENAME = "claude_adapter_inject_incompetence.py"


def path_to_claude_settings_json():
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def backup_settings_file(settings_path):
    if not os.path.isfile(settings_path):
        return None
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_path = f"{settings_path}.bak.{timestamp}"
    shutil.copyfile(settings_path, backup_path)
    return backup_path


def command_belongs_to_this_skill(command):
    return SKILL_DIRECTORY_ABSOLUTE_PATH in command and CLAUDE_ADAPTER_FILENAME in command


def remove_this_skills_entries(settings_data):
    """Strip this skill's entries from every event. Returns count removed."""
    removed_count = 0
    hooks_root = settings_data.get("hooks", {})
    for hook_event_name in list(hooks_root.keys()):
        surviving_entries = []
        for entry in hooks_root[hook_event_name]:
            surviving_hooks = [
                hook for hook in entry.get("hooks", [])
                if not command_belongs_to_this_skill(hook.get("command", ""))
            ]
            removed_count += len(entry.get("hooks", [])) - len(surviving_hooks)
            if surviving_hooks:
                entry["hooks"] = surviving_hooks
                surviving_entries.append(entry)
        if surviving_entries:
            hooks_root[hook_event_name] = surviving_entries
        else:
            del hooks_root[hook_event_name]
    return removed_count


def write_settings(settings_path, settings_data):
    with open(settings_path, "w", encoding="utf-8") as settings_file:
        json.dump(settings_data, settings_file, indent=2)
        settings_file.write("\n")


def _main():
    settings_path = path_to_claude_settings_json()
    if not os.path.isfile(settings_path):
        print(f"No settings file at {settings_path}; nothing to uninstall.")
        return 0

    with open(settings_path, "r", encoding="utf-8") as settings_file:
        settings_data = json.load(settings_file)

    removed_count = remove_this_skills_entries(settings_data)
    if removed_count == 0:
        print("Hook not found in settings; nothing to uninstall.")
        return 0

    backup_path = backup_settings_file(settings_path)
    if backup_path:
        print(f"  backed up settings -> {backup_path}")
    write_settings(settings_path, settings_data)
    print(f"Removed {removed_count} hook entry/entries. Wrote {settings_path}")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
