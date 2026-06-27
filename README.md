# Kore

**A self-learning autonomous agent that searches the web, caches knowledge in a TF-IDF vector model, synthesizes original answers, and expands its own intelligence — on your laptop, with zero cloud dependencies.**

```
  ██╗  ██╗ ██████╗ ██████╗ ███████╗
  ██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝
  █████╔╝ ██║   ██║██████╔╝█████╗
  ██╔═██╗ ██║   ██║██╔══██╗██╔══╝
  ██║  ██╗╚██████╔╝██║  ██║███████╗
  ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
  Zero-Knowledge Autonomous Agent
```

---

## Overview

Kore is a reflex-driven autonomous agent built from scratch in pure Python. Unlike modern AI systems that depend on cloud APIs or massive GPU clusters, Kore runs entirely on local hardware using lightweight statistical methods: TF-IDF vector matching, web search, Markov chain synthesis, and a background self-training daemon that retrains its model in real time.

It is designed for **students, developers, and privacy-conscious users** who want a local AI assistant that improves over time without sending data to third parties.

### How It Works

```
  You: "explain quantum entanglement"
       │
       ▼
  ┌────────────────────┐     ┌──────────────────────────────┐
  │  Ethical Guardian  │────▶│  Safety: profanity, hate     │
  │  (input check)     │     │  speech, destructive commands│
  └────────────────────┘     └──────────────────────────────┘
       │
       ▼
  ┌────────────────────┐     ┌──────────────────────────────┐
  │  TF-IDF Learner    │────▶│  ✅ Matches by word         │
  │  (vector model)    │     │  importance vectors         │
  └────────────────────┘     │  "force+acceleration"       │
       │ miss               │  → "Newton's Laws"          │
       ▼                    └──────────────────────────────┘
  ┌────────────────────┐     ┌──────────────────────────────┐
  │  Intent Analysis   │────▶│  Chat / Web Search / Code   │
  │  (reflexes.py)     │     │  Generation / Terminal / URL │
  └────────────────────┘     └──────────────────────────────┘
       │
       ▼
  ┌────────────────────┐     ┌──────────────────────────────┐
  │  4-Cycle Reflex    │────▶│  Execute, detect errors,    │
  │  Loop              │     │  self-correct, retry        │
  └────────────────────┘     └──────────────────────────────┘
```

---

## Features

### True TF-IDF Machine Learning

Kore's `IncrementalLearner` builds a real statistical model from every cached answer:

- **Term Frequency** — measures how important a word is to a document
- **Inverse Document Frequency** — measures how rare/unique a word is across all documents
- **Cosine Similarity** — finds the closest document to your query by vector angle
- **Incremental retraining** — every new cached document retrains the model immediately

This is genuine ML: fit a model on data, vectorize queries, predict the best match. No keyword lists, no pattern matching — actual weighted word importance vectors.

```
  Query: "why does an apple fall from a tree"
  → TF-IDF weighs: apple(high), fall(high), tree(medium)
  → Cosine similarity finds: "newton law gravity" entry
  → Returns: cached explanation of Newton's work
```

### Session-Based TUI

Each time you start Kore, a new **session** is created with a unique ID:

```
  kore [a3f2]> what is quantum entanglement
  kore [a3f2]> /sessions
  kore [a3f2]> /stats
  kore [a3f2]> /clear
  kore [a3f2]> exit
```

Slash commands for session management:

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/session` | Show current session info |
| `/sessions` | List all past sessions |
| `/history` | Show this session's event log |
| `/clear` | Wipe this session's history |
| `/forget` | Delete the entire knowledge cache |
| `/stats` | Memory, cache, and model stats |

### Web Search & URL Fetching

- **DuckDuckGo search** — free, no API key required
- **Direct URL fetching** — pass any URL (GitHub, Wikipedia, docs) and Kore extracts readable content

### Code Generation

Kore can generate and execute Python scripts on the fly:

| Query | Action |
|-------|--------|
| `fibonacci sequence` | Generates and runs fib function |
| `area of circle r=5` | Computes area with formula |
| `factorial of 7` | Returns 5040 |
| `check my system` | Reports CPU, RAM, OS info |
| `sort these numbers` | Interactive sorting script |

### Terminal Commands

Execute system commands with safety guardrails:

- `check memory usage` → runs `ps aux` / `free -m`
- `show network status` → runs `ip a` / `ping`
- `list files` → runs `ls -la`

### Self-Training Daemon

The `trainer.py` runs in the background and provides a second layer of learning:

- Watches the global event log for unknown queries across all sessions
- Patches Kore's internal vocabulary for topic recognition
- Retrains the TF-IDF model when new knowledge is cached
- Runs at ~0.4% CPU, polls every 30 seconds

### Ethical Guardrails

Built-in safety systems that cannot be disabled:

- **Profanity filter** — 20+ banned terms
- **Hate speech detection** — regex pattern matching
- **Destructive command prevention** — blocks `rm -rf /`, `dd if=/dev/zero`
- **Remote execution guard** — blocks `curl | sh` and `wget | bash`
- **Tone analysis** — adapts response style to emotional state
- **Self-correction limit** — max 4 retry cycles, then safe halt

### Memory Architecture

| Layer | Scope | Lifespan |
|-------|-------|----------|
| Working | Current task context | Per query |
| Episodic | Session event log | Session (cleared with `/clear`) |
| Persistent | Cross-session facts | Forever |
| Knowledge Base | Cached web answers | Forever (cleared with `/forget`) |
| TF-IDF Model | Trained vectors | Rebuilt on every new cache entry |

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **~512MB RAM**
- **Internet connection** (for web search; cached answers work offline)
- `requests` library (only dependency)

### Installation

```bash
git clone https://github.com/KasishStar/kore.git
cd kore
pip install -r requirements.txt
```

### Usage

**Interactive mode:**
```bash
python3 kore.py
```

**Single query:**
```bash
python3 kore.py "check my system memory"
python3 kore.py "explain quantum entanglement"
python3 kore.py "https://github.com/KasishStar/kore"
```

### Launch Self-Training (Optional)

```bash
cd kore && nohup python3 trainer.py > trainer.log 2>&1 &
```

---

## Project Structure

```
kore/
├── kore.py                 # Main entry point — TUI shell + reflex loop
├── trainer.py              # Background self-training daemon
├── config.json             # All user-configurable settings
├── requirements.txt        # Dependencies (requests only)
├── setup.py                # PyPI packaging
├── knowledge_base.json     # Auto-populated knowledge cache (gitignored)
├── core/
│   ├── reflexes.py         # Intent analysis, code generation, URL detection
│   ├── persona.py          # Response formatting, thought drafting
│   ├── guardian.py         # Safety: profanity, hate speech, destructive commands
│   ├── validator.py        # Action scoring and validation
│   ├── websearch.py        # DuckDuckGo search + URL page fetching
│   ├── synthesizer.py      # Markov chain text generator
│   ├── learner.py          # TF-IDF vector model (real ML)
│   ├── memory.py           # Session-aware 3-layer memory
│   └── display.py          # ANSI terminal formatting
└── .kore_memory/           # Session histories (gitignored)
    ├── history_*.jsonl     # Per-session event logs
    ├── history.jsonl       # Global event log (for trainer)
    ├── facts.json          # Cross-session persistent facts
    └── current.json        # Working context
```

---

## Configuration

All settings are in `config.json`:

```json
{
  "trainer": {
    "poll_interval_seconds": 30,
    "enabled": true
  },
  "synthesizer": {
    "markov_depth": 2,
    "max_sentences": 4,
    "min_words_fallback": 10
  },
  "kore": {
    "max_cycles": 4,
    "semantic_threshold": 0.35,
    "sandbox_timeout": 10
  }
}
```

---

## Use Cases

| User | Benefit |
|------|---------|
| **Students** | Ask about any topic — first search is live, every subsequent answer is instant from the TF-IDF model |
| **Developers** | Local coding assistant with code generation, terminal access, and doc page fetching |
| **Privacy users** | AI agent with zero telemetry, zero cloud calls, zero data collection |
| **Hobbyists** | Study agent architecture, extend with new reflexes, experiment with local ML |
| **Offline use** | After initial training, cached answers work without internet |

---

## Technical Constraints

- **Zero external ML dependencies** — no PyTorch, TensorFlow, Transformers, numpy
- **Runs on 512MB RAM** — tested on Arch Linux, works on Raspberry Pi
- **Pure Python stdlib + requests** — minimal attack surface
- **Session isolation** — each session has its own event log

---

## FAQ

**Q: Does Kore use an LLM?**  
A: No. Kore uses TF-IDF vector matching, web search, and Markov chain synthesis. No GPU, no API calls, no model downloads.

**Q: What is TF-IDF?**  
A: Term Frequency-Inverse Document Frequency. It measures how important a word is to a document relative to all other documents. This is a standard technique in information retrieval — the same math behind early search engines.

**Q: Is the TF-IDF model retrained?**  
A: Yes. Every time a new answer is cached, the model retrains immediately. The background trainer also retrains it when it processes new events.

**Q: Are sessions isolated?**  
A: Yes. Each session has its own `history_{id}.jsonl`. The knowledge base and TF-IDF model are shared across sessions.

**Q: Will Kore ever send data to the cloud?**  
A: Never. The only network traffic is DuckDuckGo searches triggered by uncached queries.

**Q: Does the trainer consume resources?**  
A: ~0.4% CPU. It polls every 30 seconds and does nothing most of the time.

**Q: Can I clear Kore's memory?**  
A: Yes. `/clear` wipes the current session. `/forget` deletes the entire knowledge cache and retrains the TF-IDF model from scratch.

---

## Limitations

- No natural language understanding — Kore matches word importance vectors, not meaning
- Responses are synthetically generated from cached patterns, not reasoned
- Markov chain text can be repetitive with very small knowledge bases
- Web search requires an internet connection

---

## License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE).

---

## About

Built by [Kasish](https://github.com/KasishStar). Kore is an exploration of what's possible with minimal dependencies and maximum constraints — proving that useful local intelligence doesn't require a million-dollar cluster.
