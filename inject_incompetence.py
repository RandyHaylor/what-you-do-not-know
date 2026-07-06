#!/usr/bin/env python3
"""Assemble the "what you do not know" reminder prompt from topics.json.

Cross-platform (no OS-specific calls). This is the engine-agnostic core: it
knows nothing about Claude hooks or OpenCode hooks. Adapters (e.g.
claude_adapter_inject_incompetence.py) call build_reminder_message() and wrap
the string in whatever shape their host expects.

Run directly to print the current message to stdout (useful for previewing
what the hook will inject):

    python3 inject_incompetence.py
"""
import json
import os
import sys

TOPICS_JSON_FILENAME = "topics.json"


def path_to_topics_json():
    """Absolute path to topics.json sitting next to this script."""
    script_directory_absolute_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory_absolute_path, TOPICS_JSON_FILENAME)


def load_topics_config():
    """Read and parse topics.json. Returns the parsed dict."""
    with open(path_to_topics_json(), "r", encoding="utf-8") as topics_file:
        return json.load(topics_file)


def build_reminder_message(topics_config=None):
    """Assemble the full agent-facing reminder string from topics.json.

    Shape:
        <preamble>
        <known_but_verify_note>
        What you don't know:
          - item
          - item
    """
    if topics_config is None:
        topics_config = load_topics_config()

    preamble = topics_config.get("preamble", "").strip()
    known_but_verify_note = topics_config.get("known_but_verify_note", "").strip()
    things_you_do_not_know = topics_config.get("things_you_do_not_know", [])

    lines = []
    if preamble:
        lines.append(preamble)
    if known_but_verify_note:
        lines.append(known_but_verify_note)
    lines.append("What you don't know (do not act as an authority on these without tool-verified proof):")
    for item in things_you_do_not_know:
        lines.append(f"  - {item}")

    return "\n".join(lines)


def _main():
    try:
        print(build_reminder_message())
    except FileNotFoundError:
        print(f"ERROR: {TOPICS_JSON_FILENAME} not found next to inject_incompetence.py",
              file=sys.stderr)
        return 1
    except json.JSONDecodeError as parse_error:
        print(f"ERROR: {TOPICS_JSON_FILENAME} is not valid JSON: {parse_error}",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(_main())
