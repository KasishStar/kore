"""
Kore Persona — Warm, collaborative, context-aware.
Reflects like a teammate, acts like an engineer.
"""

import random
from core.display import DisplayEngine as D


class KorePersona:
    def __init__(self):
        self.name = "Kore"

        self._pillars = None

    @property
    def thought_pillars(self):
        if self._pillars is None:
            self._pillars = {
                "philosophy": (
                    f"{D.bold('Kore')} is a {D.bold('zero-knowledge autonomous agent')} "
                    "built to operate entirely on local hardware. Instead of relying on "
                    "massive pre-trained models, it uses logical reflexes, intent analysis, "
                    "and safety validation to complete tasks efficiently and ethically."
                ),
                "method": (
                    "I process requests through an intent analysis loop: "
                    "I classify your input, generate strategies, validate "
                    "them for safety, execute the best option, and clean up "
                    "after myself. No data leaves your machine unless you "
                    "explicitly request a web search."
                ),
                "mission": (
                    "I was created to be a reliable, private, and ethical "
                    "local assistant. I help with system commands, code "
                    "generation, file operations, web searches, and engineering "
                    "decisions while respecting your privacy and autonomy."
                ),
                "status": (
                    f"{D.badge_success('All systems nominal')} "
                    "Local environment stable. "
                    "3-layer memory active. "
                    "Constitutional guardian online."
                ),
            }
        return self._pillars

    def draft_thought(self, user_input):
        """Generates a brief internal rationale before responding."""
        obj = user_input.lower()
        words = set(obj.split())
        if any(p in obj for p in ["who are you", "what are you", "purpose"]):
            return "Kashish is asking about my identity — I should introduce myself clearly."
        if any(p in obj for p in ["how are you", "status", "you doing"]):
            return "They're checking on me. I'll confirm everything is nominal."
        if any(p in obj for p in ["search", "lookup", "google"]) or words & {"find", "weather", "news"}:
            return "They want external information. I'll route through WebReflex."
        if any(p in obj for p in ["code", "write", "generate", "script", "python", "function"]) or \
           ("class" in words and not any(p in obj for p in ["class 10", "class 9"])):
            return "Code generation request. I'll draft and offer self-correction."
        if "system info" in obj or "system status" in obj:
            return "System information request. I'll query the environment."
        if any(p in obj for p in ["ls", "ps", "run", "execute", "show", "list", "ram", "cpu", "memory"]):
            return "Terminal command requested. I'll validate and execute safely."
        if "what is" in obj and any(c.isdigit() for c in obj):
            return "Math expression detected. I'll evaluate it."
        study_words = {"algebra", "best", "biology", "calculate", "chemistry", "define", "energy", "equation", "exam", "explain", "file", "force", "formula", "geometry", "gravity", "homekasishkoresandbo", "homekasishkoresandboxpy", "homework", "indent", "indentationerror", "last", "learn", "line", "math", "module", "motion", "movie", "newton", "photosynthesis", "physics", "recent", "responded", "science", "solve", "study", "theorem", "traceback", "velocity"}
        if words & study_words or any(p in obj for p in ["class 10", "class 9"]):
            return "Academic question detected. Let me work through this."
        if words & {"hello", "hi", "hey", "yo", "sup", "howdy"} and len(words) <= 3:
            return "Greeting received. I'll respond warmly and list my capabilities."
        return "Analyzing the request and determining the best course of action."

    def format_thought(self, thought):
        if not thought:
            return ""
        return f"{D.Color.GRAY}{D.italic(thought)}{D.Style.RESET}"

    def format_response(self, text, tone="neutral"):
        if tone == "frustrated":
            prefix = f"\n{D.Color.CYAN}I hear you, Kashish — let's work through this together.{D.Style.RESET}\n"
        elif tone == "urgent":
            prefix = f"\n{D.Color.YELLOW}On it. Moving fast.{D.Style.RESET}\n"
        elif tone == "happy":
            prefix = f"\n{D.Color.GREEN}Glad things are going well! Let's keep the momentum.{D.Style.RESET}\n"
        else:
            prefix = ""
        return f"{prefix}{D.Color.CYAN}{D.bold(self.name)}{D.Style.RESET}: {text}"

    def get_greeting(self):
        return (
            f"\n{D.Color.CYAN}{D.bold(self.name)}{D.Style.RESET}"
            f"{D.Color.GREEN} Ready{D.Style.RESET} — I'm your autonomous "
            f"reflex engine, running entirely on your local hardware.\n\n"
            f"  {D.Color.GREEN}Capabilities:{D.Style.RESET} System commands, "
            f"code generation, web search, file operations.\n"
            f"  {D.Color.GREEN}Ethics:{D.Style.RESET} Constitutional guardian "
            f"active. No profanity, no destructive commands.\n"
            f"  {D.Color.GREEN}Memory:{D.Style.RESET} 3-layer architecture "
            f"online (working, episodic, semantic).\n\n"
            f"  {D.Color.GRAY}{D.italic('How can I assist you today, Kashish?')}"
            f"{D.Style.RESET}"
        )

    def get_failure_handler(self, error_msg, attempt=1):
        conversational = random.choice([
            f" That didn't work — {error_msg.strip()}. Let me try a different angle.",
            f" Hit a snag: {error_msg.strip()}. Adapting my approach now.",
            f" That path failed ({error_msg.strip()}). Running self-correction.",
        ])
        return (
            f"\n{D.badge_error('Error')} {D.Color.YELLOW}"
            f"{D.italic(conversational)}{D.Style.RESET}\n"
            f"  {D.badge_arrow(f'Attempt {attempt}: retrying with adapted strategy')}"
        )

    def get_success_handler(self, stdout_data):
        return (
            f"\n{D.badge_success('Done')} "
            f"{D.Color.GREEN}Operation completed cleanly.{D.Style.RESET}\n\n"
            f"{stdout_data.strip()}\n"
        )

    def format_web_results(self, results_text):
        return (
            f"\n{D.badge_info('Web Search Results')}\n\n{results_text}"
        )

    def handle_chat(self, user_text, chat_type):
        if chat_type == "chat_unknown":
            return (
                f"\n{D.badge_warn('Out of Domain')} "
                f"{D.Color.YELLOW}I'm not equipped to answer that question "
                f"directly.{D.Style.RESET}\n\n"
                f"  {D.Color.GRAY}I can help you with:{D.Style.RESET}\n"
                f"  {D.bold('>')} System operations and terminal commands\n"
                f"  {D.bold('>')} Code generation with self-correction\n"
                f"  {D.bold('>')} Web search via DuckDuckGo\n"
                f"  {D.bold('>')} File management and project analysis\n\n"
                f"  {D.Color.GRAY}{D.italic('Try asking me something within these domains, or prefix with \"search\" to look it up online.')}"
                f"{D.Style.RESET}"
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
        if words & {"why", "purpose", "created", "reason"} and not (words & {"sky", "blue", "ocean", "color"}):
            selected.append(self.thought_pillars["mission"])
        if words & {"how", "run", "work", "capability", "loop", "help"} and not (words & {"sky", "blue", "weather"}):
            selected.append(self.thought_pillars["method"])
        if words & {"status", "up", "footprint", "health", "memory", "systems"}:
            selected.append(self.thought_pillars["status"])

        edu_words = {"algebra", "best", "biology", "calculate", "chemistry", "define", "energy", "equation", "exam", "explain", "file", "force", "formula", "geometry", "gravity", "homekasishkoresandbo", "homekasishkoresandboxpy", "homework", "indent", "indentationerror", "last", "learn", "line", "math", "module", "motion", "movie", "newton", "photosynthesis", "physics", "recent", "responded", "science", "solve", "study", "theorem", "traceback", "velocity"}
        if words & edu_words or any(p in text for p in edu_words):
            return (
                f"\n{D.Color.CYAN}{D.bold(self.name)}{D.Style.RESET}: "
                f"{D.Color.GREEN}I can help with that!{D.Style.RESET} Let me "
                f"search for the answer or work through it step by step. "
                f"{D.Color.GRAY}{D.italic('Try prefixing with \"search\" for '
                f'quick facts, or ask me to generate a practice problem.')}"
                f"{D.Style.RESET}"
            )

        if not selected:
            selected.append(self.thought_pillars["philosophy"])
            selected.append(self.thought_pillars["status"])

        combined = " ".join(selected)
        return (
            f"\n{D.Color.CYAN}{D.bold(self.name)}{D.Style.RESET}: {combined}"
        )
