import random

class KorePersona:
    def __init__(self):
        self.name = "Kore"

        self.peer_validations = [
            "I am ready to assist. Let me analyze your request carefully.",
            "Standing by. I will follow your instructions precisely.",
            "Kore online. I understand the task. Proceeding with caution and care.",
            "Systems ready. I will complete this task exactly as specified.",
            "Awaiting your direction. I aim to be helpful, harmless, and honest."
        ]

        self.candid_pivots = [
            "I encountered an unexpected result. Let me adjust my approach.",
            "That did not work as planned. I will try a different method.",
            "There seems to be an issue. I am analyzing the error and adapting.",
            "Let me reconsider the strategy and attempt a safer alternative."
        ]

        self.success_logs = [
            "Task completed successfully. Here are the results:",
            "Done. The operation finished without issues. Output below:",
            "Completed as requested. Please find the results:"
        ]

        self.thought_pillars = {
            "philosophy": (
                "Kore is a zero-knowledge autonomous agent built to operate "
                "entirely on local hardware. Instead of relying on massive "
                "pre-trained models, it uses logical reflexes, intent analysis, "
                "and safety validation to complete tasks efficiently and ethically."
            ),
            "method": (
                "Kore processes requests through an intent analysis loop: "
                "it classifies your input, generates strategies, validates "
                "them for safety, executes the best option, and cleans up "
                "after itself. No data leaves your machine unless you ask "
                "for a web search."
            ),
            "mission": (
                "Kore was created to be a reliable, private, and ethical "
                "local assistant. It helps with system commands, code "
                "generation, file operations, web searches, and engineering "
                "decisions while respecting your privacy and autonomy."
            ),
            "status": (
                "All systems are functioning normally. The local environment "
                "is stable, and Kore is ready for your next instruction."
            )
        }

    def get_validation(self):
        return f"\n✨ [{self.name}]: {random.choice(self.peer_validations)}"

    def get_greeting(self):
        return (
            f"\n⚡ [{self.name}]: Hello. I am Kore, an autonomous local agent. "
            "I can run system commands, generate code, search the web, and "
            "help with engineering tasks. Everything stays on your machine. "
            "How may I assist you today?"
        )

    def get_failure_handler(self, error_msg):
        pivot = random.choice(self.candid_pivots)
        return (
            f"\n⚠️ [{self.name}]: {pivot}\n"
            f"   Details: {error_msg.strip()}\n"
        )

    def get_success_handler(self, stdout_data):
        success = random.choice(self.success_logs)
        return f"\n✅ [{self.name}]: {success}\n\n{stdout_data.strip()}\n"

    def format_web_results(self, results_text):
        return f"\n🌐 [{self.name}]: Here is what I found:\n\n{results_text}"

    def handle_philosophical_chat(self, user_text, chat_type):
        if chat_type == "chat_unknown":
            return (
                f"\n⚠️ [{self.name}]: I am not equipped to answer that question. "
                "My knowledge is limited to system operations, code generation, "
                "file management, and web search. Please ask me something "
                "within these domains, or request a web search."
            )

        text = user_text.lower().strip().rstrip("?!.,;:")
        words = set(text.split())
        greeting_words = {"hi", "hello", "hey", "yo", "sup", "howdy", "good", "morning", "evening"}

        if words & greeting_words:
            return self.get_greeting()

        selected = []

        if "who are you" in text or "what are you" in text:
            selected.append(self.thought_pillars["philosophy"])
            selected.append(self.thought_pillars["mission"])

        if "how are you" in text or "you doing" in text:
            selected.append(self.thought_pillars["status"])

        if words & {"why", "purpose", "created", "reason"}:
            if not (words & {"sky", "blue", "ocean", "color"}):
                selected.append(self.thought_pillars["mission"])

        if words & {"how", "run", "work", "capability", "loop", "help"}:
            if not (words & {"sky", "blue", "weather"}):
                selected.append(self.thought_pillars["method"])

        if words & {"status", "up", "footprint", "health"}:
            selected.append(self.thought_pillars["status"])

        if not selected:
            selected.append(self.thought_pillars["philosophy"])
            selected.append(self.thought_pillars["status"])

        combined = " ".join(selected)
        return f"\n🧠 [{self.name}]: {combined}"
