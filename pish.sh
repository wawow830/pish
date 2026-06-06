#!/usr/bin/env bash
set -euo pipefail

# pish — natural language → bash → execute
# Wraps the pi coding agent harness to generate shell commands.

OLLAMA_EXT="${HOME}/.pi/agent/npm/node_modules/pi-ollama-cloud/index.ts"
DEFAULT_MODEL="gemma4"

SYSTEM_PROMPT="You are a precise bash command generator. Convert the user's natural language description into the exact bash command(s) needed. Respond with ONLY raw bash commands. No markdown code fences. No explanations. No commentary. Output must be valid bash that can be executed directly."

model="$DEFAULT_MODEL"
thinking=""
dry_run=false

# Parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      model="$2"
      shift 2
      ;;
    --thinking)
      thinking="$2"
      shift 2
      ;;
    --dry-run)
      dry_run=true
      shift
      ;;
    --help|-h)
      cat <<'EOF'
Usage: pish [--model <name>] [--thinking <level>] [--dry-run] <prompt>

  --model <name>      LLM model (default: gemma4)
  --thinking <level>  off, minimal, low, medium, high, xhigh
  --dry-run           Preview command without executing

Examples:
  pish "list all docker containers"
  pish --model deepseek-v3.2 --thinking low "find large files"
  echo "show disk usage" | pish
EOF
      exit 0
      ;;
    --)
      shift
      break
      ;;
    -*)
      echo "Unknown option: $1" >&2
      echo "Usage: pish [--model <name>] [--thinking <level>] [--dry-run] <prompt>" >&2
      exit 1
      ;;
    *)
      break
      ;;
  esac
done

# Collect prompt from remaining args or stdin
prompt="$*"
if [[ -z "$prompt" ]] && [[ ! -t 0 ]]; then
  prompt=$(cat)
fi

if [[ -z "$prompt" ]]; then
  echo "Usage: pish [--model <name>] [--thinking <level>] [--dry-run] <prompt>" >&2
  exit 1
fi

# Build pi command using positional params so word-splitting is safe
set -- pi \
  --print \
  --no-session \
  --no-tools \
  --no-skills \
  --no-prompt-templates \
  --no-context-files \
  --no-themes \
  --mode text \
  --system-prompt "$SYSTEM_PROMPT"

# Lock down to only the ollama-cloud extension so fast models work
if [[ -f "$OLLAMA_EXT" ]]; then
  set -- "$@" --no-extensions -e "$OLLAMA_EXT"
fi

if [[ -n "$thinking" ]]; then
  set -- "$@" --thinking "$thinking"
fi

set -- "$@" --model "$model" "$prompt"

# Generate
echo -ne "🧠 generating...\r" >&2
output=$("$@" 2>&1) || {
  echo -ne "                    \r" >&2
  echo "$output" >&2
  exit 1
}
echo -ne "                    \r" >&2

# Strip deprecation warning line if present
if [[ "$output" == Deprecation* ]]; then
  output=$(printf '%s\n' "$output" | tail -n +2)
fi

# Strip markdown fences
output=$(printf '%s\n' "$output" | sed -E 's/^```(bash|sh|shell)?[[:space:]]*//')
output=$(printf '%s\n' "$output" | sed -E 's/[[:space:]]*```$//')

# Trim leading/trailing whitespace on each line and collapse empty ends
output=$(printf '%s\n' "$output" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')

# Remove leading/trailing blank lines from the whole block
output=$(printf '%s\n' "$output" | sed -e '/./,$!d' | tac | sed -e '/./,$!d' | tac)

if [[ -z "$output" ]]; then
  echo "No command generated." >&2
  exit 1
fi

# Display
printf '%s\n' "$output" | while IFS= read -r line; do
  echo "> $line"
done

if [[ "$dry_run" == true ]]; then
  echo "(Dry run — not executed)"
  exit 0
fi

# Confirm and execute
read -r -p "Execute? [y/n]: " answer || true
if [[ "$answer" =~ ^[Yy](es)?$ ]]; then
  bash -c "$output"
else
  echo "Aborted."
  exit 0
fi
