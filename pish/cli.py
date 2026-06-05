#!/usr/bin/env python3
"""
pish — natural language → bash → execute
Wraps the pi coding agent harness to generate shell commands.
"""

import argparse
import os
import re
import subprocess
import sys

DEFAULT_MODEL = "gemma4"
SYSTEM_PROMPT = (
    "You are a precise bash command generator. "
    "Convert the user's natural language description into the exact bash command(s) needed. "
    "Respond with ONLY raw bash commands. No markdown code fences. No explanations. "
    "No commentary. Output must be valid bash that can be executed directly."
)

OLLAMA_EXT = os.path.expanduser("~/.pi/agent/npm/node_modules/pi-ollama-cloud/index.ts")


def generate_command(prompt: str, model: str | None) -> str:
    cmd = [
        "pi",
        "--print",
        "--no-session",
        "--no-tools",
        "--no-skills",
        "--no-prompt-templates",
        "--no-context-files",
        "--no-themes",
        "--mode", "text",
        "--system-prompt", SYSTEM_PROMPT,
    ]
    # Lock down to only the ollama-cloud extension so fast models like gemma4 work
    if os.path.isfile(OLLAMA_EXT):
        cmd += ["--no-extensions", "-e", OLLAMA_EXT]
    if model:
        cmd += ["--model", model]
    cmd += [prompt]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr or result.stdout, file=sys.stderr)
        sys.exit(result.returncode)

    output = result.stdout.strip()

    # Strip deprecation warning line
    lines = output.splitlines()
    if lines and "Deprecation warning" in lines[0]:
        lines = lines[1:]
    output = "\n".join(lines).strip()

    # Strip markdown fences if the model disobeyed
    output = re.sub(r"^```(?:bash|sh|shell)?\s*", "", output)
    output = re.sub(r"\s*```$", "", output)
    output = output.strip()

    if not output:
        print("No command generated.", file=sys.stderr)
        sys.exit(1)

    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pish",
        description="Natural language → bash → execute",
    )
    parser.add_argument("prompt", nargs="*", help="Description of what to do")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"LLM model (default: {DEFAULT_MODEL})")
    parser.add_argument("--dry-run", action="store_true", help="Preview command without executing")
    args = parser.parse_args()

    if args.prompt:
        prompt = " ".join(args.prompt)
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    if not prompt:
        parser.print_help()
        sys.exit(1)

    print("🧠 generating...", end="\r", file=sys.stderr)
    command = generate_command(prompt, args.model)
    sys.stderr.write(" " * 20 + "\r")
    sys.stderr.flush()

    # Display
    for line in command.splitlines():
        print(f"> {line}")

    if args.dry_run:
        print("(Dry run — not executed)")
        sys.exit(0)

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
