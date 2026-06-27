# Kore 🧠⚡

**Zero-Knowledge Autonomous Agent — A Reflex-Driven Local Coding Assistant**

Kore is an experimental, hyper-lightweight autonomous agent that throws away the multi-gigabyte brute-force paradigm of modern AI. Instead of loading a 40GB+ model into RAM, Kore boots with a minimal set of hardwired digital "reflexes" to think, generate code, execute commands, and adapt to errors — all on your local machine with zero cloud dependencies.

## Philosophy

Modern AI relies on **Dense Pre-Trained Weights** — forcing consumer hardware to run billions of parameters just to get simple logic answers. Kore scales compute at **Test-Time** instead. It mimics how human infants are born with foundational reflexes (sight, error-crying, mimicry) rather than pre-stored facts, using an automated sandbox search loop to figure out solutions natively in real-time.

## Architecture

```
                    ┌─────────────────────────┐
                    │      User Input         │
                    └───────────┬─────────────┘
                                │
                                ▼
              ┌──────────────────────────────────┐
              │      analyze_intent()            │
              │  (action-token probability loop) │
              └───────┬──────────────────┬───────┘
                      │                  │
             ┌────────▼────────┐  ┌──────▼─────────┐
             │  Terminal/Code  │  │    Chat/Query   │
             └────────┬────────┘  └──────┬─────────┘
                      │                  │
             ┌────────▼────────┐  ┌──────▼─────────┐
             │  mutate_        │  │  semantic       │
             │  hypotheses()   │  │  closeness      │
             └────────┬────────┘  │  check          │
                      │           └──────┬─────────┘
             ┌────────▼────────┐  ┌──────▼─────────┐
             │  validator      │  │  persona        │
             │  (safety check) │  │  (response)     │
             └────────┬────────┘  └────────────────┘
                      │
             ┌────────▼────────┐
             │  execute /      │◄── error feedback loop
             │  sandbox        │
             └────────┬────────┘
                      │
                      ▼
             ┌────────────────┐
             │  purge memory  │
             └────────────────┘
```

## The 4-Step Agentic Loop

1. **Ingest (Sight Reflex):** Captures your objective and environment state.
2. **Mutate (Brainstorming Reflex):** Generates multiple strategy branches based on intent — chat, terminal command, or code generation.
3. **Validate (Saab Layer):** Scores each branch for safety and relevance; rejects dangerous commands.
4. **Execute & Adapt:** Runs the winning strategy in a sandbox. On error, feeds the failure back into the mutation loop for self-correction. On success, displays output and purges all temporary state.

## Features

- **Intent Routing** — Automatically separates conversational chat from system commands and code generation using action-token probability.
- **Semantic Domain Awareness** — Uses character-level cosine similarity to know when a question is outside its scope, avoiding hallucination.
- **Dynamic Code Generation** — Writes Python scripts on-the-fly based on your request, executes them, and self-corrects on error.
- **Self-Correction Loop** — When a command or script fails, Kore reads the error and mutates its approach up to 4 times.
- **Safety Validation** — Built-in Saab Validator blocks dangerous commands (rm -rf /, mkfs, fork bombs, etc.).
- **Memory Purge** — After every task, all temporary weights and sandbox files are wiped clean — zero residue.
- **Interactive Shell** — Run `python3 kore.py` for a REPL-like session, or pass a query directly.

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/kore.git
cd kore
python3 kore.py "find top 5 processes using CPU"
```

### Interactive Mode

```bash
python3 kore.py
```

Then type commands like:
- `check my system memory`
- `write a script to generate fibonacci series`
- `who are you?`
- `find all python files in this directory`
- `exit` to quit

## Requirements

- Python 3.10+
- Linux / macOS (Windows via WSL)
- No GPU required. No cloud API keys. No 40GB model downloads.
- Works on as little as 512MB RAM for basic reflex mode.

## Roadmap

- [ ] Add persistent skill modules (Android sensors via Termux, smart home)
- [ ] MicroPython port for ESP32 / Raspberry Pi Pico
- [ ] Plugin system for user-defined motor skills
- [ ] Web interface for mobile control
- [ ] Multi-agent orchestration

## License

MIT — free to use, modify, and distribute.

---

Built by Kashish — breaking the fourth wall, one reflex at a time.
