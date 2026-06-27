"""
Kore Persona — Direct, architectural, structured conversations.
"""

import random
from core.display import DisplayEngine as D


class KorePersona:
    def __init__(self):
        self.name = "Kore"

        self.peer_validations = [
            "I am ready. Let me analyze this systematically.",
            "Understood. Here is my architectural approach.",
            "Let me break this down step by step.",
            "Processing your request through the reflex loop.",
            "Standing by to execute. I will follow exactly as specified."
        ]

        self.candid_pivots = [
            "The environment returned an unexpected result. Let me adapt.",
            "That path did not work. Switching to an alternative strategy.",
            "Error detected. Running the self-correction loop now.",
            "The system pushed back. Recalculating my approach."
        ]

        self.success_logs = [
            "Task completed. Here is the result:",
            "Done. The operation finished cleanly. Output:",
            "Objective reached. No errors detected. Result:"
        ]

        self._pillars = None

    @property
    def thought_pillars(self):
        if self._pillars is None:
            self._pillars = {
                "philosophy": (
                    f"{D.bold('Kore')} is a {D.bold('zero-knowledge autonomous agent')} "
                    "built to operate entirely on local hardware. "
                    "Instead of relying on massive pre-trained models, "
                    "it uses logical reflexes, intent analysis, "
                    "and safety validation to complete tasks efficiently and ethically."
                ),
                "method": (
                    "Kore processes requests through an intent analysis loop: "
                    "it classifies your input, generates strategies, validates "
                    "them for safety, executes the best option, and cleans up "
                    "after itself. No data leaves your machine unless you explicitly "
                    "request a web search."
                ),
                "mission": (
                    "Kore was created to be a reliable, private, and ethical "
                    "local assistant. It helps with system commands, code "
                    "generation, file operations, web searches, and engineering "
                    "decisions while respecting your privacy and autonomy. "
                    "Everything runs locally. No cloud, no tracking, no bloat."
                ),
                "status": (
                    f"{D.badge_success('All systems nominal')} "
                    "Local environment stable. "
                    "3-layer memory active. "
                    "Constitutional guardian online. "
                    "Ready for your next instruction."
                ),
            }
        return self._pillars

    def get_validation(self):
        return f"\n{D.Color.CYAN}▸{D.Style.RESET} {D.bold(self.name)}: {D.italic(random.choice(self.peer_validations))}"

    def get_greeting(self):
        return (
            f"\n  {D.Color.GREEN}Ready{D.Style.RESET} — Kore is an autonomous reflex engine "
            "running entirely on your local hardware.\n"
            f"  {D.Color.GREEN}Capabilities{D.Style.RESET} — System commands, code generation, "
            "web search, file operations.\n"
            f"  {D.Color.GREEN}Ethics{D.Style.RESET} — Constitutional guardian active. "
            "No profanity, no destructive commands.\n"
            f"  {D.Color.GREEN}Memory{D.Style.RESET} — 3-layer architecture online "
            f"(working, episodic, semantic).\n\n"
            f"  {D.dim('How can I assist you today?')}"
        )

    def get_failure_handler(self, error_msg):
        return (
            f"\n{D.badge_error('Error')} {D.Color.YELLOW}{D.italic(error_msg.strip())}{D.Style.RESET}\n"
            f"  {D.badge_arrow('Retrying with adapted strategy')}"
        )

    def get_success_handler(self, stdout_data):
        return (
            f"\n{D.badge_success('Complete')}\n\n"
            f"{stdout_data.strip()}\n"
        )

    def format_web_results(self, results_text):
        return f"\n{D.badge_info('Web Search Results')}\n\n{results_text}"

    def handle_philosophical_chat(self, user_text, chat_type):
        if chat_type == "chat_unknown":
            return (
                f"\n{D.badge_warn('Out of Domain')} "
                f"{D.Color.YELLOW}I am not equipped to answer that question.{D.Style.RESET}\n\n"
                f"  {D.dim('My knowledge is limited to:')}\n"
                f"  {D.bold('▸')} System operations and terminal commands\n"
                f"  {D.bold('▸')} Code generation with self-correction\n"
                f"  {D.bold('▸')} Web search via DuckDuckGo\n"
                f"  {D.bold('▸')} File management and project analysis\n\n"
                f"  {D.italic('Try asking me something within these domains,')}\n"
                f"  {D.italic('or prefix your question with \"search\" to look it up online.')}"
            )

        text = user_text.lower().strip().rstrip("?!.,;:")
        words = set(text.split())
        greeting_words = {"hi", "hello", "hey", "yo", "sup", "howdy"}

        if words & greeting_words:
            return self.get_greeting()

        selected = []

        if "who are you" in text or "what are you" in text:
            selected.append(self.thought_pillars["philosophy"])
        if "how are you" in text or "you doing" in text:
            selected.append(self.thought_pillars["status"])
        if words & {"why", "purpose", "created", "reason"}:
            if not (words & {"sky", "blue", "ocean", "color"}):
                selected.append(self.thought_pillars["mission"])
        if words & {"how", "run", "work", "capability", "loop", "help"}:
            if not (words & {"sky", "blue", "weather"}):
                selected.append(self.thought_pillars["method"])
        if words & {"status", "up", "footprint", "health", "memory", "systems"}:
            selected.append(self.thought_pillars["status"])

        if not selected:
            selected.append(self.thought_pillars["philosophy"])
            selected.append(self.thought_pillars["status"])

        combined = " ".join(selected)
        return f"\n{D.Color.CYAN}▸{D.Style.RESET} {D.bold(self.name)}: {combined}"
