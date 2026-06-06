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
# Describe what you want (uses quality gemma4 model by default)
pish "create a directory called backups and copy all .txt files into it"

# Shell quoting tips (fish/zsh/bash)
pish 'create *.txt for each letter of the alphabet'

# Need speed? Use the fast model (~1.9s vs ~2.3s)
pish --fast "echo hello"

# Pipe a prompt in
echo "list all docker containers" | pish

# Preview without executing
pish --dry-run "rm -rf important_folder"

# Use a specific model
pish --model deepseek-v3.2 "find all large files"

# Control how hard the model thinks
pish --thinking low "list running processes"
pish --thinking off "echo hello"
```

**Workflow:**
1. `pish` sends your description to the pi LLM harness with a strict "bash only" system prompt
2. The generated command is printed with a `>` prefix
3. You confirm with `y` (or abort with `n`)
4. If confirmed, `pish` executes the command via bash

**Options:**
- `--model <name>` — override the LLM (default: `gemma4`)
- `--fast` — use `rnj-1:8b` for faster generation (~1.9s)
- `--thinking <level>` — control reasoning depth: `off`, `minimal`, `low`, `medium`, `high`, `xhigh`
- `--dry-run` — preview the command without executing

---

## Model selection

Benchmarked on ollama-cloud with the prompt "create a txt file for each letter a through z":

| model | speed | quality | best for |
|---|---|---|---|
| `rnj-1:8b` | ~1.9 s | clean, uses absolute paths | `--fast` flag |
| `gemma4` | ~2.3 s | clean, relative paths | **default** |
| `qwen3-coder-next` | ~1.9 s | wraps in backticks | avoid |
| `deepseek-v3.2` | ~8 s | very thorough | complex tasks |

---

## How it works

`pish` invokes `pi` in **print mode** with everything locked down except the ollama-cloud extension (so models resolve correctly):

```bash
pi --print --no-session --no-tools --no-skills \
   --no-prompt-templates --no-context-files \
   --no-themes --mode text \
   --no-extensions -e ~/.pi/agent/npm/node_modules/pi-ollama-cloud/index.ts \
   --model gemma4 --system-prompt "..." "your prompt"
```

---

## Safety

`pish` **never executes without explicit `y` confirmation.** Review every command before approving. The LLM can hallucinate — you are the final safety layer.

---

## License

MIT
