#!/usr/bin/env python3
"""
Kore — Zero-Knowledge Autonomous Agent
A reflex-driven, self-correcting local agent with 3-layer memory
and formatted terminal output.
"""

import sys
import os
import json
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


def check_knowledge_cache(query):
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
        label = D.colorize('Synthesized', D.Color.MAGENTA) if response != cached else D.colorize('Knowledge Base', D.Color.GREEN)
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
            response = persona.handle_chat(action["payload"], action["type"])
            print(persona.format_response(response, tone))
            event_type = "chat_unknown" if action["type"] == "chat_unknown" else "chat"
            memory.log_event(event_type, f"Responded to: {goal_prompt[:60]}")
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
            print(f"\n  {D.colorize('Page Content', D.Color.GREEN)}")
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
    print(D.divider())
    print(f"  {D.highlight(' KORE v0.3 ', D.Color.BG_CYAN, D.Color.BLACK)} "
          f"{D.bold('Interactive Shell')}")
    print(D.divider())
    print(f"  {D.dim('Type your request or \"exit\" to quit.')}\n")

    while True:
        try:
            user_input = input(f"  {D.Color.CYAN}kore>{D.Style.RESET} ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print(f"\n  {D.badge_info('Shutdown')} Memory preserved. Goodbye.\n")
                break
            run_engine(user_input, memory=memory)
            print()
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {D.badge_info('Shutdown')} Goodbye.\n")
            break


def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        run_engine(prompt)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
