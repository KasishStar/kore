# Kore

**A self-learning autonomous agent that searches the web, caches knowledge, synthesizes original answers, and expands its own intelligence — on your laptop, with zero cloud dependencies.**

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

Kore is a reflex-driven autonomous agent built from scratch in pure Python. Unlike modern AI systems that depend on cloud APIs or massive GPU clusters, Kore runs entirely on local hardware using lightweight statistical methods: keyword matching, web search, Markov chain synthesis, and a background self-training daemon.

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
  │  Knowledge Cache   │────▶│  ✅ Instant if already known │
  │  (knowledge_base   │     │  → Synthesize or return raw  │
  │   .json lookup)    │     │                              │
  └────────────────────┘     └──────────────────────────────┘
       │ miss
       ▼
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

### Self-Training System (Core Innovation)

The `trainer.py` daemon runs in the background and automatically expands Kore's intelligence:

1. **Monitors** `history.jsonl` for `chat_unknown` events — queries Kore didn't recognize
2. **Searches the web** via DuckDuckGo for relevant information
3. **Summarizes** results into a concise 3-sentence explanation
4. **Caches** the summary in `knowledge_base.json` for instant future lookups
5. **Patches** Kore's keyword vectors so it recognizes the topic next time

```
  First ask:  "what is quantum entanglement"
              → Kore: "I don't know"
              → Trainer searches web, caches summary, patches vocabulary

  Second ask: "what is quantum entanglement"
              → Kore: Instant answer from knowledge_base.json
              → Markov chain generates an original 3-5 sentence response
```

Over time, Kore builds a **local encyclopedia** of every topic you've asked about. No API calls, no cloud costs, no privacy leaks.

### Markov Text Synthesis

When a cached answer is found, Kore doesn't just copy-paste it. The `synthesizer.py` module builds a **Markov chain** from all cached text and generates statistically unique responses:

- Analyzes word transition patterns (e.g., "Newton" → "force" → "motion")
- Generates 3-5 sentence explanations that are technically new sentences
- Falls back to the raw cached summary when the knowledge base is too small

### Web Search & URL Fetching

- **DuckDuckGo search** — free, no API key required
- **Direct URL fetching** — pass any URL (GitHub, Wikipedia, docs) and Kore extracts readable content:
  ```
  kore> https://github.com/KasishStar/kore
  → Returns page title, description, file listing
  ```

### Code Generation

Kore can generate and execute Python scripts on the fly:

| Query | Action |
|-------|--------|
| `fibonacci sequence` | Generates and runs fib function |
| `area of circle r=5` | Computes area with formula |
| `factorial of 7` | Returns 5040 |
| `check my system` | Reports CPU, RAM, OS info |
| `sort these numbers` | Interactive sorting script |
| `multiplication table` | Generates table for any number |

### Terminal Commands

Execute system commands with safety guardrails:
- `check memory usage` → runs `ps aux` / `free -m`
- `show network status` → runs `ip a` / `ping`
- `list files` → runs `ls -la`

### URL & Page Fetching

Pass any URL to Kore and it fetches the readable content:

```
kore> https://github.com/KasishStar/kore
kore> https://en.wikipedia.org/wiki/Physics
kore> https://docs.python.org/3/
```

### Ethical Guardrails

Built-in safety systems that cannot be disabled:

- **Profanity filter** — 20+ banned terms, blocked in input and output
- **Hate speech detection** — regex pattern matching on both user input and responses
- **Tone analysis** — adapts response style to emotional state (frustrated, urgent, neutral)
- **Destructive command prevention** — blocks `rm -rf /`, `dd if=/dev/zero`, format commands
- **Remote execution guard** — blocks `curl | sh` and `wget | bash` patterns
- **Self-correction limit** — max 4 retry cycles, then safe halt

### 3-Layer Memory

| Layer | Scope | Persistence |
|-------|-------|-------------|
| Working | Current task context | Cleared after each task |
| Episodic | Recent interactions | Session duration |
| Persistent | Learned patterns | `history.jsonl` on disk |

### Semantic Matching

When searching the knowledge cache, Kore uses three levels of matching:

1. **Exact** — query matches a cached concept key directly
2. **Partial word overlap** — shared keywords between query and cached concept
3. **Semantic closeness** — `difflib.SequenceMatcher` ratio (threshold 0.35)

This means "force and motion" will match "Newton's Laws" even without exact keyword overlap.

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **~512MB RAM**
- **Internet connection** (for web search and URL fetching; cached answers work offline)
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

### Launch Self-Training (Recommended)

After every system boot, run the trainer in the background:
```bash
cd kore && nohup python3 trainer.py > trainer.log 2>&1 &
```

Verify it's running:
```bash
ps aux | grep trainer.py
```

Watch it learn:
```bash
tail -f patches/log.json
```

The trainer polls `history.jsonl` every 30 seconds, processes `chat_unknown` events, and automatically expands Kore's knowledge.

---

## Project Structure

```
kore/
├── kore.py                 # Main entry point — interactive shell + reflex loop
├── trainer.py              # Self-training daemon (background process)
├── config.json             # All user-configurable settings
├── requirements.txt        # Dependencies (requests only)
├── setup.py                # PyPI packaging
├── knowledge_base.json     # Auto-populated knowledge cache (gitignored)
├── trainer.log             # Trainer output (gitignored)
├── core/
│   ├── reflexes.py         # Intent analysis, code generation, URL detection
│   ├── persona.py          # Response formatting, thought drafting
│   ├── guardian.py         # Safety: profanity, hate speech, destructive command blocking
│   ├── validator.py        # Action scoring and validation
│   ├── websearch.py        # DuckDuckGo search + URL page fetching
│   ├── synthesizer.py      # Markov chain text generator
│   ├── memory.py           # 3-layer memory management
│   └── display.py          # ANSI terminal formatting
├── patches/                # Training patch audit log (gitignored)
│   └── log.json
└── .kore_memory/           # Session history (gitignored)
    └── history.jsonl
```

---

## Configuration

All settings are in `config.json`:

```json
{
  "trainer": {
    "poll_interval_seconds": 30,
    "max_patch_words": 500,
    "enabled": true
  },
  "synthesizer": {
    "markov_depth": 2,
    "max_sentences": 4,
    "min_sentences": 2,
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
| **Students** | Build a personal study assistant that learns your syllabus. Ask about Newton's Laws, photosynthesis, polynomials — first search is live, every subsequent answer is instant. |
| **Developers** | Local coding assistant with code generation, terminal access, and doc page fetching. No data leaves your machine. |
| **Privacy-conscious users** | AI agent with zero telemetry, zero cloud calls, zero data collection. |
| **Hobbyists** | Study agent architecture, extend with new reflexes, experiment with local AI without GPU requirements. |
| **Offline environments** | After initial training, cached answers work without internet. |

---

## Technical Constraints

- **Zero external ML dependencies** — no PyTorch, TensorFlow, Transformers, or numpy
- **Runs on 512MB RAM** — tested on Arch Linux, works on Raspberry Pi
- **Under 2000 lines** (excluding trainer) — easy to read, modify, and extend
- **No class exceeds 250 lines** — modular by design
- **Pure Python stdlib + requests** — minimal attack surface

---

## FAQ

**Q: Does Kore use an LLM?**  
A: No. Kore uses keyword vectors, web search, and Markov chain synthesis. No GPU, no API calls, no model downloads.

**Q: Will Kore ever send data to the cloud?**  
A: Never. The only network traffic is DuckDuckGo searches triggered by uncached queries. Your data stays on your machine.

**Q: How long until Kore is "trained"?**  
A: There is no finish line. Kore learns incrementally with every `chat_unknown` event. ~20-30 queries will cover most of a class 10 syllabus. The trainer runs forever and keeps learning.

**Q: Does the trainer consume resources?**  
A: ~0.4% CPU. It polls every 30 seconds and does nothing most of the time.

**Q: Can I turn off self-training?**  
A: Yes. Simply don't launch `trainer.py`. Kore works fine without it — it just won't auto-expand.

**Q: Does the Markov chain ever produce nonsense?**  
A: If the generated response is fewer than 10 words, it automatically falls back to the raw cached summary. This ensures reliability even when the knowledge base is small.

**Q: Can Kore read GitHub pages?**  
A: Yes. Pass any URL and Kore will fetch and display the readable content. This works for GitHub repos, Wikipedia articles, documentation pages, etc.

---

## Limitations

- No natural language understanding — Kore matches keywords, not meaning
- No context retention across sessions (except the trainer's knowledge base)
- Responses are synthetically generated from cached patterns, not reasoned
- Web search requires an internet connection
- Markov chain text can be repetitive with very small knowledge bases

---

## License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE).

---

## About

Built by [Kasish](https://github.com/KasishStar). Kore is an exploration of what's possible with minimal dependencies and maximum constraints — proving that useful local intelligence doesn't require a million-dollar cluster.
