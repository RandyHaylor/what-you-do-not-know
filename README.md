This skill is a tool that constantly reminds claude agents what the DO NOT KNOW to prevent them from acting like they are authorities on subjects when they have done no research and have no real concrete knowledge and have not actually verified claims they make.

SKILL.md - minimal, explains the skill and how to update skill settings
topics.json - the list of things the agent 'knows' and 'doesn't know' - can be updated by user/agent
inject_incompetence.py - cross platform script that assembles and returns the prompt from topics.json

claude-specific files
claude_adapter_inject_incompetence.py - cross platform script that is the layer that reacts to the claude hooks
claude_install.py - cross platform tool to install the hook from user ~/.claude/settings.json
claude_uninstall.py - cross platform tool to uninstall the hook

opencode-specific files
*same as claude-specific but for opencode (may not be the exact same shape, depends on opencode's exposed hooks/methods - may not be hook based)


Required in SKILL.md:

The 4 stages of learning
1) Unconscious incompetence –  You don’t know what you don’t know.
2) Conscious incompetence – You know what you don’t know.
3) Conscious competence – You know, but using your knowledge requires a lot of concentration.
4) Unconscious competence – You know so well that you can use your knowledge instinctively.

The ai agent spends a lot of time at 1). If asked very directly and insistently, it will agree to 2), discover or search for answers and acheive 3).

It has 4) for many things, but those are basic things, not advanced topics, yet it acts like it has 4) for many complex things, which in reality puts it back to 1) in practice.

This skill's main goal is to elevate the base ai agent's awareness to have 2) as a baseline.
This is acheived currently by a hook that injects a small string with every tool call and every user prompt submit, via claude hooks.
It will simply trigger on a pre-tool-use and user prompt submit hook and run the script, which injects the message with the context (see source-of-truth skill for how it injects to agent-visible context) AND it will echo the message so the user can see it too (so they know it's being sent AND they can see what the current content of it is).


The message should look something like:
You are in the second stage of learning for most things - You know what you don't know.  What you don't know: <fill in from list here>

List of topics 'not known':
<we need to do some trial and error to figure out what works here>
NOT KNOWN: The first thing you suspect to be the problem is actually the problem without concrete proof.
NOT KNOWN: The best current solution to a design or troubleshooting problem is without a real web search first.
NOT KNOWN: That you know better than the user about any given topic.

