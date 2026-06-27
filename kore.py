#!/usr/bin/env python3
"""
Kore — Zero-Knowledge Autonomous Agent
A reflex-driven, self-correcting local agent with 3-layer memory
and formatted terminal output.
"""

import sys
import os
import json
import re
import difflib
import subprocess
from core.reflexes import InfantReflexes
from core.persona import KorePersona
from core.validator import SaabValidator
from core.websearch import WebReflex
from core.guardian import EthicalGuardian
from core.memory import MemoryManager
from core.display import DisplayEngine as D
from core.synthesizer import MarkovSynthesizer
from core.learner import IncrementalLearner

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_FILE = os.path.join(BASE_DIR, "knowledge_base.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

CONFIG = {}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            CONFIG = json.load(f)
    except (json.JSONDecodeError, Exception):
        pass

SEMANTIC_THRESHOLD = CONFIG.get("kore", {}).get("semantic_threshold", 0.35)
MAX_CYCLES = CONFIG.get("kore", {}).get("max_cycles", 4)
SANDBOX_TIMEOUT = CONFIG.get("kore", {}).get("sandbox_timeout", 10)


def _summarize(snippets, max_sentences=3):
    text = " ".join(s.strip() for s in snippets if s.strip())
    if not text:
        return None
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for s in sentences:
        s = s.strip()
        if len(s) < 15:
            continue
        result.append(s)
        if len(result) >= max_sentences:
            break
    return " ".join(result) if result else None


_learner = None


def get_learner():
    global _learner
    if _learner is None:
        _learner = IncrementalLearner()
        _learner.fit()
    return _learner


def check_knowledge_cache(query):
    learner = get_learner()
    match = learner.predict(query, threshold=0.08)
    if match:
        return match
    if not os.path.exists(KNOWLEDGE_FILE):
        return None
    try:
        with open(KNOWLEDGE_FILE, "r") as f:
            kb = json.load(f)
    except (json.JSONDecodeError, Exception):
        return None
    q = query.lower().strip()
    cached = kb.get(q)
    if cached:
        return cached
    best_match = None
    best_score = 0.0
    for concept, summary in kb.items():
        words = concept.split()
        if any(w in q for w in words if len(w) > 3) and any(w in concept for w in q.split() if len(w) > 3):
            return summary
        score = difflib.SequenceMatcher(None, q, concept).ratio()
        if score > best_score:
            best_score = score
            best_match = summary
    if best_score >= SEMANTIC_THRESHOLD and best_match:
        return best_match
    return None


_synthesizer = None


def get_synthesizer():
    global _synthesizer
    if _synthesizer is None:
        sc = CONFIG.get("synthesizer", {})
        _synthesizer = MarkovSynthesizer(
            depth=sc.get("markov_depth", 2),
            max_sentences=sc.get("max_sentences", 4),
            min_sentences=sc.get("min_sentences", 2),
            min_words=sc.get("min_words_fallback", 10),
        )
        _synthesizer.build()
    return _synthesizer


def run_engine(goal_prompt, memory=None):
    reflex = InfantReflexes()
    persona = KorePersona()
    validator = SaabValidator()
    web = WebReflex()
    guardian = EthicalGuardian()
    if memory is None:
        memory = MemoryManager()

    memory.set_working_context(objective=goal_prompt, cycle=0)
    context_prompt = memory.build_context_prompt(goal_prompt)

    tone = guardian.analyze_tone(goal_prompt)
    is_safe, reason, _ = guardian.validate_action(
        {"type": "chat", "payload": goal_prompt}, user_input=goal_prompt
    )
    if not is_safe:
        print(f"\n{D.badge_error('Blocked')} {reason}")
        return

    cached = check_knowledge_cache(goal_prompt)
    if cached:
        synth = get_synthesizer()
        response = synth.generate(topic=goal_prompt) or cached
        label = D.color('Synthesized', D.Color.MAGENTA) if response != cached else D.color('Knowledge Base', D.Color.GREEN)
        tag = D.dim('(generated)') if response != cached else D.dim('(cached)')
        print(D.divider())
        print(f"  {D.highlight(' KORE v0.3 ', D.Color.BG_CYAN, D.Color.BLACK)} "
              f"{D.bold('Zero-Knowledge Autonomous Agent')}")
        print(D.divider())
        thought = persona.draft_thought(goal_prompt)
        print(f"\n  {persona.format_thought(thought)}")
        print(f"\n  {D.dim('Objective:')} {D.bold(goal_prompt)}")
        print(f"\n  {label} {tag}")
        print(f"\n  {response}")
        print(D.divider())
        if memory:
            memory.store_episodic(goal_prompt, response)
        return

    print(D.divider())
    print(f"  {D.highlight(' KORE v0.3 ', D.Color.BG_CYAN, D.Color.BLACK)} "
          f"{D.bold('Zero-Knowledge Autonomous Agent')}")
    print(D.divider())

    thought = persona.draft_thought(goal_prompt)
    print(f"\n  {persona.format_thought(thought)}")

    print(f"\n  {D.dim('Objective:')} {D.bold(goal_prompt)}")

    solved = False
    cycle = 1
    max_cycles = MAX_CYCLES
    last_error = None

    while not solved and cycle <= max_cycles:
        memory.set_working_context(cycle=cycle, last_error=last_error)

        hypotheses = reflex.mutate_hypotheses(
            {"objective": goal_prompt}, failure_log=last_error
        )

        if not hypotheses:
            print(f"\n  {D.badge_warn('Halted')} No hypotheses generated.")
            break

        action = validator.process_supervision(hypotheses)

        if action["type"] == "safe_halt":
            print(f"\n  {D.badge_error('Blocked')} {action['payload']}")
            break

        is_safe, reason, action = guardian.validate_action(action)
        if not is_safe:
            print(f"\n  {D.badge_error('Blocked')} {reason}")
            break

        if action["type"] in ("chat_internal", "chat_unknown"):
            if action["type"] == "chat_unknown":
                print(f"\n  {D.badge_arrow('Learning')} Searching the web...")
                results = web.search(goal_prompt)
                snippets = []
                for r in results:
                    text = r.get("snippet") or r.get("title") or ""
                    if text.strip():
                        snippets.append(text)
                summary = _summarize(snippets) if snippets else None
                if summary:
                    concept = " ".join(re.findall(r"[A-Za-z0-9']+", goal_prompt.lower()))[:120]
                    try:
                        with open(KNOWLEDGE_FILE, "r") as f:
                            kb = json.load(f)
                    except:
                        kb = {}
                    if concept not in kb:
                        kb[concept] = summary
                        os.makedirs(os.path.dirname(KNOWLEDGE_FILE), exist_ok=True)
                        with open(KNOWLEDGE_FILE, "w") as f:
                            json.dump(kb, f, indent=2)
                        get_learner().add_document(concept, summary)
                    synth = get_synthesizer()
                    synth.build()
                    response = synth.generate(topic=goal_prompt) or summary
                    print(f"\n  {D.color('Learned', D.Color.GREEN)}"
                          f" {D.dim('(cached for next time)')}")
                    print(f"\n  {response}")
                else:
                    response = persona.handle_chat(action["payload"], action["type"])
                    print(persona.format_response(response, tone))
                memory.log_event("chat_unknown", f"Responded to: {goal_prompt[:60]}")
            else:
                response = persona.handle_chat(action["payload"], action["type"])
                print(persona.format_response(response, tone))
                memory.log_event("chat", f"Responded to: {goal_prompt[:60]}")
            solved = True
            break

        if action["type"] == "web_search":
            query = action["payload"]
            print(f"\n  {D.badge_arrow('Web Search')} {D.italic(query)}")
            results = web.search(query)
            formatted = web.format_results(results)
            print(persona.format_web_results(formatted))
            memory.log_event("search", f"Searched: {query[:60]}")
            solved = True
            break

        if action["type"] == "fetch_url":
            url = action["payload"]
            print(f"\n  {D.badge_arrow('Fetch URL')} {D.italic(url)}")
            content = web.fetch_url(url)
            print(f"\n  {D.color('Page Content', D.Color.GREEN)}")
            print(f"\n  {content[:2000]}")
            memory.log_event("fetch", f"Fetched: {url[:60]}")
            solved = True
            break

        if action["type"] == "execute_code":
            target_file = action.get("file", "kore_sandbox.py")
            print(f"\n  {D.badge_arrow('Code')} Generating -> {D.bold(target_file)}")
            memory.log_event("code_gen", f"Writing: {target_file}")

            with open(target_file, "w") as f:
                f.write(action["payload"])

            print(f"  {D.badge_arrow('Run')} Executing")
            memory.log_event("exec", f"Running: {target_file}")

            try:
                result = subprocess.run(
                    ["python3", target_file],
                    capture_output=True,
                    text=True,
                    timeout=SANDBOX_TIMEOUT
                )
                if result.returncode == 0:
                    print(persona.get_success_handler(result.stdout))
                    memory.log_event("exec_success", "Code ran cleanly")
                    solved = True
                else:
                    last_error = result.stderr or "Non-zero exit code."
                    print(persona.get_failure_handler(last_error, cycle))
                    memory.log_event("error", last_error[:100], success=False)
            except subprocess.TimeoutExpired:
                last_error = f"Execution timed out (>{SANDBOX_TIMEOUT}s)."
                print(persona.get_failure_handler(last_error, cycle))
                memory.log_event("error", last_error, success=False)
            except Exception as e:
                last_error = str(e)
                print(persona.get_failure_handler(last_error, cycle))
                memory.log_event("error", str(e)[:100], success=False)

            if os.path.exists(target_file):
                os.remove(target_file)

            cycle += 1
            continue

        print(f"\n  {D.badge_arrow('Command')} {D.dim(action['payload'])}")
        memory.log_event("terminal", f"Running: {action['payload'][:60]}")

        try:
            result = subprocess.run(
                action["payload"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=SANDBOX_TIMEOUT
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    print(persona.get_success_handler(output))
                else:
                    print(f"\n  {D.badge_success('Done')} Command executed (no output).")
                memory.log_event("cmd_success", action["payload"][:60])
                solved = True
            else:
                last_error = result.stderr or f"Exit code: {result.returncode}"
                print(persona.get_failure_handler(last_error, cycle))
                memory.log_event("error", last_error[:100], success=False)
        except subprocess.TimeoutExpired:
            last_error = f"Command timed out (>{SANDBOX_TIMEOUT}s)."
            print(persona.get_failure_handler(last_error, cycle))
            memory.log_event("error", last_error, success=False)
        except Exception as e:
            last_error = str(e)
            print(persona.get_failure_handler(last_error, cycle))
            memory.log_event("error", str(e)[:100], success=False)

        cycle += 1

    memory.set_working_context(status="complete" if solved else "failed")
    memory.clear_working_context()

    sandbox = getattr(reflex, "sandbox_file", None)
    if sandbox and os.path.exists(sandbox):
        os.remove(sandbox)

    print()
    print(D.divider())
    if solved:
        print(f"  {D.badge_success('Task Complete')} Memory purged. Standing by.")
    else:
        print(f"  {D.badge_warn('Halted')} Max cycles reached. Safe termination.")
    print(D.divider())


def interactive_mode():
    memory = MemoryManager()
    sid = memory.session_id
    trainer_check()
    print(D.divider())
    print(f"  {D.highlight(' KORE v0.5 ', D.Color.BG_CYAN, D.Color.BLACK)} "
          f"{D.bold('Autonomous Reflex Engine')}")
    print(D.divider())
    tag = "trainer on" if trainer_running() else "trainer off"
    print(f"  {D.dim('Session:')} {D.bold(sid)}  "
          f"{D.dim('Type /help · /train · exit')}")
    print(f"  {D.dim('Trainer:')} {D.color(tag, D.Color.GREEN if trainer_running() else D.Color.GRAY)}"
          f"  {D.dim('KB:')} {D.bold(str(kb_entry_count()))}\n")

    while True:
        try:
            user_input = input(f"  {D.Color.CYAN}❯{D.Style.RESET} ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q", "/exit"):
                print(f"\n  {D.badge_info('Bye')} Session {sid} saved.\n")
                break
            if user_input.startswith("/"):
                handle_command(user_input, memory)
                continue
            run_engine(user_input, memory=memory)
            print()
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {D.badge_info('Bye')} Session {sid} saved.\n")
            break


def handle_command(cmd, memory):
    parts = cmd.strip().split()
    command = parts[0].lower()

    if command == "/help":
        print(f"\n  {D.bold('Commands')}")
        print(f"  {D.dim('─' * 40)}")
        for c, d in [
            ("/help", "Show this menu"),
            ("/train", "Start/stop background trainer"),
            ("/session", "Current session info"),
            ("/sessions", "List all sessions"),
            ("/history", "Session event log"),
            ("/stats", "Memory and cache stats"),
            ("/clear", "Wipe session history"),
            ("/forget", "Delete knowledge cache"),
            ("exit", "Quit Kore"),
        ]:
            print(f"  {D.bold(c):10} {D.dim(d)}")
        print()

    elif command == "/session":
        sid = memory.session_id
        events = memory.get_session_events(limit=1)
        print(f"\n  {D.bold('Current Session')}")
        print(f"  {D.dim('ID:')}       {sid}")
        print(f"  {D.dim('Events:')}   {len(memory.get_session_events())}")
        print(f"  {D.dim('Memory:')}   {memory.memory_dir}")
        if events:
            print(f"  {D.dim('Started:')}  {events[0]['timestamp']}")
        print()

    elif command == "/sessions":
        sessions = memory.list_sessions()
        if not sessions:
            print(f"\n  {D.dim('No sessions found.')}\n")
        else:
            print(f"\n  {D.bold(f'Sessions ({len(sessions)})')}")
            for s in sessions:
                marker = "→" if s == memory.session_id else " "
                print(f"  {marker} {s}")
            print()

    elif command == "/clear":
        memory.clear_session()
        print(f"\n  {D.badge_success('Cleared')} Session history wiped.\n")

    elif command == "/forget":
        if os.path.exists(KNOWLEDGE_FILE):
            os.remove(KNOWLEDGE_FILE)
            print(f"\n  {D.badge_success('Forgotten')} Knowledge cache deleted.\n")
        else:
            print(f"\n  {D.dim('Nothing to forget.')}\n")

    elif command == "/stats":
        kb_size = 0
        kb_entries = 0
        if os.path.exists(KNOWLEDGE_FILE):
            kb_size = os.path.getsize(KNOWLEDGE_FILE)
            try:
                with open(KNOWLEDGE_FILE) as f:
                    kb_entries = len(json.load(f))
            except:
                pass
        mem_size = 0
        if os.path.exists(memory.memory_dir):
            for f in os.listdir(memory.memory_dir):
                fp = os.path.join(memory.memory_dir, f)
                if os.path.isfile(fp):
                    mem_size += os.path.getsize(fp)
        session_events = len(memory.get_session_events())
        learner = get_learner()
        print(f"\n  {D.bold('Kore Stats')}")
        print(f"  {D.dim('─' * 40)}")
        print(f"  {D.dim('Knowledge base:')}  {kb_entries} entries ({kb_size} bytes)")
        print(f"  {D.dim('TF-IDF model:')}    {'loaded' if learner.fitted else 'empty'}")
        print(f"  {D.dim('Session events:')}  {session_events}")
        print(f"  {D.dim('Memory folder:')}   {mem_size} bytes")
        print()

    elif command == "/train":
        subcmd = parts[1] if len(parts) > 1 else ""
        running = trainer_running()
        if subcmd in ("stop", "off"):
            if running:
                for proc in os.popen("ps aux | grep trainer.py"):
                    line = proc.strip()
                    if "trainer.py" in line and "grep" not in line and "def" not in line:
                        try:
                            os.kill(int(line.split()[1]), 15)
                        except:
                            pass
                print(f"\n  {D.badge_info('Trainer')} Stopped.\n")
            else:
                print(f"\n  {D.dim('Trainer not running.')}\n")
        else:
            if running:
                print(f"\n  {D.color('Trainer is running', D.Color.GREEN)}"
                      f" {D.dim('- use /train stop to stop')}\n")
            else:
                trainer_check()
                print(f"\n  {D.color('Trainer launched', D.Color.GREEN)}\n")

    elif command == "/history":
        events = memory.get_session_events(limit=20)
        if not events:
            print(f"\n  {D.dim('No events in this session.')}\n")
        else:
            print(f"\n  {D.bold(f'Session History ({len(events)} events)')}")
            for e in events[-10:]:
                ts = e.get("timestamp", "?")[11:19]
                t = e.get("type", "?")
                s = e.get("summary", "")[:60]
                print(f"  {D.dim(ts)} [{t}] {s}")
            print()

    else:
        print(f"\n  {D.badge_warn('Unknown')} Command not found. Try /help\n")


def trainer_running():
    for proc in os.popen("ps aux | grep trainer.py"):
        line = proc.strip()
        if "trainer.py" in line and "grep" not in line and "def" not in line:
            return True
    return False


def trainer_check():
    if trainer_running():
        return
    pid = os.fork()
    if pid == 0:
        os.setsid()
        script = os.path.join(BASE_DIR, "trainer.py")
        log = os.path.join(BASE_DIR, "trainer.log")
        with open(log, "a") as f:
            os.dup2(f.fileno(), 1)
            os.dup2(f.fileno(), 2)
        os.execvp("python3", ["python3", script])
        os._exit(0)


def kb_entry_count():
    if not os.path.exists(KNOWLEDGE_FILE):
        return 0
    try:
        with open(KNOWLEDGE_FILE) as f:
            return len(json.load(f))
    except:
        return 0


def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        run_engine(prompt)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
