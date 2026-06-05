# 🐟 pish

**Natural language → bash → execute.**

`pish` is a tiny bash script that wraps the [pi](https://pi.dev) coding agent harness. Describe what you want in plain English, and `pish` generates the bash command, asks for confirmation, and runs it.

---

## Installation

### Prerequisites

- [pi](https://pi.dev) must be installed and authenticated

### One-liner install

```bash
curl -L https://raw.githubusercontent.com/wawow830/pish/main/pish.sh -o ~/.local/bin/pish
chmod +x ~/.local/bin/pish
```

Or clone and symlink:

```bash
git clone https://github.com/wawow830/pish.git
cd pish
ln -sf "$(pwd)/pish.sh" ~/.local/bin/pish
```

---

## Usage

```bash
# Describe what you want (uses fast gemma4 model by default)
pish "create a directory called backups and copy all .txt files into it"

# Shell quoting tips (fish/zsh/bash)
pish 'create *.txt for each letter of the alphabet'

# Pipe a prompt in
echo "list all docker containers" | pish

# Preview without executing
pish --dry-run "rm -rf important_folder"

# Use a different model
pish --model deepseek-v3.2 "find all large files"
```

**Workflow:**
1. `pish` sends your description to the pi LLM harness with a strict "bash only" system prompt
2. The generated command is printed with a `>` prefix
3. You confirm with `y` (or abort with `n`)
4. If confirmed, `pish` executes the command via bash

**Options:**
- `--model <name>` — override the LLM (default: `gemma4`)
- `--dry-run` — preview the command without executing

---

## How it works

`pish` invokes `pi` in **print mode** with everything locked down except the ollama-cloud extension (so fast models like `gemma4` resolve correctly):

```bash
pi --print --no-session --no-tools --no-skills \
   --no-prompt-templates --no-context-files \
   --no-themes --mode text \
   --no-extensions -e ~/.pi/agent/npm/node_modules/pi-ollama-cloud/index.ts \
   --model gemma4 --system-prompt "..." "your prompt"
```

The default model is `gemma4` (~2–3 s) because it was the fastest model in benchmarks that still produces clean, correct bash. You can override with any model your `pi` install has authenticated.

---

## Safety

`pish` **never executes without explicit `y` confirmation.** Review every command before approving. The LLM can hallucinate — you are the final safety layer.

---

## License

MIT
