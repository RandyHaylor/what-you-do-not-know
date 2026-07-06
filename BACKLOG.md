# Backlog

## OpenCode support (not yet implemented)

The engine-agnostic core (`inject_incompetence.py` + `topics.json`) is already
host-neutral and should be reused as-is. What remains is the OpenCode adapter
layer, mirroring the Claude-specific files:

- [ ] `opencode_adapter_inject_incompetence.py` — reacts to OpenCode's
      hook/extension mechanism, injects the reminder into agent-visible context,
      and echoes it to the user. **Note:** OpenCode's exposed hooks/methods may
      differ from Claude's and may not be hook-based; the adapter shape depends
      on what OpenCode exposes. Research this before implementing.
- [ ] `opencode_install.py` — install into OpenCode's config.
- [ ] `opencode_uninstall.py` — remove from OpenCode's config.

Until then, only Claude Code is supported.

## Open questions from the README

- [ ] Trial-and-error the exact wording / topic list in `topics.json` to find
      what actually changes agent behavior (the README flagged this as unsettled).
