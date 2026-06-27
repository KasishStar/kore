#!/usr/bin/env python3
"""
Kore — Zero-Knowledge Autonomous Agent
A reflex-driven, self-correcting local agent that writes code,
runs commands, and adapts to errors without cloud dependencies.
"""

import sys
import os
import subprocess
from core.reflexes import InfantReflexes
from core.persona import KorePersona
from core.validator import SaabValidator


def run_engine(goal_prompt):
    reflex = InfantReflexes()
    persona = KorePersona()
    validator = SaabValidator()

    border = "=" * 60

    print(border)
    print(f"KORE AUTONOMOUS AGENT // v0.2 // Zero-Knowledge Reflex Engine")
    print(border)

    context = reflex.ingest_environment(goal_prompt)
    print(persona.get_validation())
    print(f"   Objective: '{goal_prompt}'")

    solved = False
    cycle = 1
    max_cycles = 4
    last_error = None

    while not solved and cycle <= max_cycles:
        hypotheses = reflex.mutate_hypotheses(context, failure_log=last_error)

        if not hypotheses:
            print(f"\n[{self.name}]: No hypotheses generated. Halting.")
            break

        action = validator.process_supervision(hypotheses)

        if action["type"] == "safe_halt":
            print(f"\n⛔ [{persona.name}]: {action['payload']}")
            break

        # ── CHAT PATH ────────────────────────────────────────────
        if action["type"] in ("chat_internal", "chat_unknown"):
            response = persona.handle_philosophical_chat(
                action["payload"], action["type"]
            )
            print(response)
            solved = True
            break

        # ── CODE GENERATION PATH ─────────────────────────────────
        if action["type"] == "execute_code":
            target_file = action.get("file", "kore_sandbox.py")
            print(f"\n[Cycle {cycle}/{max_cycles}] Generating code → {target_file}")

            with open(target_file, "w") as f:
                f.write(action["payload"])

            print(f" -> Executing: python3 {target_file}")

            try:
                result = subprocess.run(
                    ["python3", target_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    print(persona.get_success_handler(result.stdout))
                    solved = True
                else:
                    last_error = result.stderr or "Non-zero exit code."
                    print(persona.get_failure_handler(last_error))
                    print(" -> Triggering self-correction loop...")
            except subprocess.TimeoutExpired:
                last_error = "Execution timed out (>10s)."
                print(persona.get_failure_handler(last_error))
            except Exception as e:
                last_error = str(e)
                print(persona.get_failure_handler(last_error))

            if os.path.exists(target_file):
                os.remove(target_file)

            cycle += 1
            continue

        # ── TERMINAL COMMAND PATH ────────────────────────────────
        print(f"\n[Cycle {cycle}/{max_cycles}] Executing strategy...")
        print(f" -> Command: {action['payload']}")

        try:
            result = subprocess.run(
                action["payload"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    print(persona.get_success_handler(output))
                else:
                    print(f"\n⚡ [{persona.name}]: Command executed cleanly (no output).")
                solved = True
            else:
                last_error = result.stderr or f"Exit code: {result.returncode}"
                print(persona.get_failure_handler(last_error))
                print(" -> Adapting and retrying...")
        except subprocess.TimeoutExpired:
            last_error = "Command timed out (>10s)."
            print(persona.get_failure_handler(last_error))
        except Exception as e:
            last_error = str(e)
            print(persona.get_failure_handler(last_error))

        cycle += 1

    # ── CLEANUP ─────────────────────────────────────────────────
    reflex.local_weights.clear() if hasattr(reflex, 'local_weights') else None
    if os.path.exists(reflex.sandbox_file):
        os.remove(reflex.sandbox_file)

    print()
    print(border)
    if solved:
        print("TASK COMPLETE // Goal reached. Local variable matrix purged clean.")
    else:
        print("ENGINE HALTED // Max cycles reached. Safe termination.")
    print(border)


def interactive_mode():
    border = "=" * 60
    print(border)
    print("KORE INTERACTIVE SHELL // Type 'exit' or 'quit' to stop")
    print(border)
    print()

    while True:
        try:
            user_input = input("kore> ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Kore shutting down. Memory purged. Goodbye.")
                break
            run_engine(user_input)
            print()
        except (KeyboardInterrupt, EOFError):
            print("\nKore shutting down. Goodbye.")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        run_engine(prompt)
    else:
        interactive_mode()
