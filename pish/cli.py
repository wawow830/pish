#!/usr/bin/env python3
"""
pish — natural language → bash → execute
Wraps the pi coding agent harness to generate shell commands.
"""

import re
import subprocess
import sys

SYSTEM_PROMPT = (
    "You are a precise bash command generator. "
    "Convert the user's natural language description into the exact bash command(s) needed. "
    "Respond with ONLY raw bash commands. No markdown code fences. No explanations. "
    "No commentary. Output must be valid bash that can be executed directly."
)


def generate_command(prompt: str) -> str:
    cmd = [
        "pi",
        "--print",
        "--no-session",
        "--no-tools",
        "--no-extensions",
        "--no-skills",
        "--no-prompt-templates",
        "--no-context-files",
        "--no-themes",
        "--mode", "text",
        "--system-prompt", SYSTEM_PROMPT,
        prompt,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(result.returncode)

    output = result.stdout.strip()

    # Strip markdown fences if the model disobeyed
    output = re.sub(r"^```(?:bash|sh|shell)?\s*", "", output)
    output = re.sub(r"\s*```$", "", output)
    output = output.strip()

    if not output:
        print("No command generated.", file=sys.stderr)
        sys.exit(1)

    return output


def main() -> None:
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        print("Usage: pish <prompt>", file=sys.stderr)
        sys.exit(1)

    if not prompt:
        print("Usage: pish <prompt>", file=sys.stderr)
        sys.exit(1)

    print("🧠 generating...", end="\r", file=sys.stderr)
    command = generate_command(prompt)
    sys.stderr.write(" " * 20 + "\r")
    sys.stderr.flush()

    # Display
    for line in command.splitlines():
        print(f"> {line}")

    # Confirm
    try:
        answer = input("Execute? [y/n]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(1)

    if answer in ("y", "yes"):
        sys.exit(subprocess.run(["bash", "-c", command]).returncode)
    else:
        print("Aborted.")
        sys.exit(0)


if __name__ == "__main__":
    main()
