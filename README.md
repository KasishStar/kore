# Kore 🧠⚡

**Zero-Knowledge Autonomous Agent — v0.3**

Kore is an experimental, hyper-lightweight autonomous agent that runs entirely on your local machine. No cloud, no GPU, no 40GB model downloads. Just clean logical reflexes.

## What Kore Does

Kore can:
- **Run terminal commands** — check system stats, network, files
- **Generate and execute code** — write Python scripts on the fly, self-correct errors
- **Search the web** — fetch real-time information via DuckDuckGo
- **Hold conversations** — answer questions about its identity, purpose, and methods
- **Detect its limits** — refuses to hallucinate answers outside its domain

## Safety & Ethics

Kore has a built-in **Ethical Guardian** that:
- Blocks profanity and hate speech in both input and output
- Detects destructive system commands
- Adapts its tone to your emotional state (frustrated, urgent, happy)
- Always responds in proper English
- Never assumes — follows instructions exactly as given

## Architecture

```
             ┌──────────────┐
             │  User Input  │
             └──────┬───────┘
                    │
             ┌──────▼───────┐
             │   Guardian   │  ← Profanity, hate speech, tone check
             └──────┬───────┘
                    │
             ┌──────▼───────┐
             │  Intent      │  ← Chat / Terminal / Code / Web
             │  Analysis    │
             └──────┬───────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
   ┌────────┐ ┌──────────┐ ┌──────────┐
   │ Chat   │ │ Terminal │ │ Code     │
   │ Persona│ │ Sandbox  │ │ Generator│
   └────────┘ └────┬─────┘ └────┬─────┘
                   │            │
             ┌─────▼──────┐     │
             │ Web Search │     │
             └─────┬──────┘     │
                   │            │
             ┌─────▼───────────▼─┐
             │  Error Feedback   │  ← Self-correction loop
             │  & Adaptation     │
             └───────┬───────────┘
                     │
             ┌───────▼───────────┐
             │  Memory Purge     │  ← Zero residue after every task
             └───────────────────┘
```

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/kore.git
cd kore
python3 kore.py "check my system memory"
```

### Interactive Mode

```bash
python3 kore.py
kore> who are you?
kore> check memory usage
kore> search the web for latest python version
kore> write a fibonacci script
kore> exit
```

### Examples

| Command | Result |
|---------|--------|
| `hi` | Greeting message |
| `who are you?` | Kore's identity and purpose |
| `check my system memory` | Runs `ps aux` sorted by CPU |
| `write a fibonacci script` | Generates, runs, outputs `[0,1,1,2,3,5,8,13,21,34]` |
| `who is the president of france?` | Searches web, returns Wikipedia summary |
| `why is the sky blue?` | Detects out-of-domain, refuses to hallucinate |

## Requirements

- Python 3.10+
- `requests` library (for web search)
- Linux / macOS (Windows via WSL)
- No GPU. No cloud API keys. No 40GB downloads.

## Files

```
kore/
├── kore.py              # Main entry point with 4-step agentic loop
├── core/
│   ├── reflexes.py      # Intent analysis, code generation, semantic routing
│   ├── persona.py       # Companion personality and conversational responses
│   ├── validator.py     # Safety checks and command scoring
│   ├── websearch.py     # Web search via DuckDuckGo API
│   ├── guardian.py      # Ethical guardian: profanity filter, tone analysis
│   └── __init__.py
├── README.md
└── .gitignore
```

## Roadmap

- [x] Terminal command execution with safety validation
- [x] Dynamic code generation with self-correction
- [x] Intent-based routing (chat vs terminal vs code)
- [x] Semantic domain awareness (knows what it doesn't know)
- [x] Web search capability
- [x] Ethical guardian with profanity filter and empathetic tone
- [ ] Plugin system for user-defined skills
- [ ] MicroPython port for ESP32 / Raspberry Pi Pico
- [ ] Web interface for mobile control

## License

MIT — free to use, modify, and distribute.

---

Built by Kashish — breaking the fourth wall, one reflex at a time.
