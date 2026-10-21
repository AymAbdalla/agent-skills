#!/usr/bin/env python3
"""Claude Code UserPromptSubmit hook: remind Claude that aym-skills is the default workflow.

Draft, not registered. It ignores the prompt text, reads nothing, writes nothing,
makes no network calls, and always exits 0 so it can never block a prompt.
Plain-text stdout on exit 0 is added as context next to the prompt.
"""
import sys

# Factual wording on purpose: Claude Code's docs warn that imperative,
# system-style hook text can trip prompt-injection defenses.
NUDGE = (
    "The default workflow for actionable work is the aym-skills plugin. "
    "Its work-my-way skill routes each phase (clarify, plan, build, check, ship) "
    "and the user expects a stop card after every phase. Simple factual questions "
    "do not need it."
)


def main():
    try:
        sys.stdin.read()  # drain the event JSON; the prompt is not inspected
    except Exception:
        pass
    print(NUDGE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
