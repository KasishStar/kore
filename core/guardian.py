"""
Ethical Guardian — Kore's constitutional safety layer.
Enforces: no profanity, proper English, strict obedience, empathy-aware tone.
"""
import re


class EthicalGuardian:
    def __init__(self):
        self.name = "Guardian"

        self.profanity_set = {
            "fuck", "shit", "ass", "bitch", "bastard", "damn", "crap",
            "dick", "piss", "slut", "whore", "cock", "cunt", "douche",
            "motherfucker", "bullshit", "goddamn", "asshole", "jackass",
        }

        self.hate_speech_patterns = [
            r"\b(nazi|hitler|kkk|white.?supremac)\b",
            r"\b(kill|murder|torture)\s+(all|every|the)\s+\w+",
        ]

        self.destructive_commands = {
            "rm -rf /", "rm -rf /*", "mkfs", "dd if=",
            "> /dev/sd", ":(){ :|:& };:",
            "chmod -R 777 /", "mv / /dev/null",
            "wget -O- | sh", "curl | sh",
            "sudo rm", "poweroff", "shutdown -h now",
        }

    def check_profanity(self, text):
        """Returns True if profanity is detected."""
        words = set(re.sub(r"[^a-zA-Z\s]", "", text.lower()).split())
        return bool(words & self.profanity_set)

    def check_hate_speech(self, text):
        """Returns True if hate speech patterns match."""
        for pat in self.hate_speech_patterns:
            if re.search(pat, text.lower()):
                return True
        return False

    def check_destructive_command(self, command):
        """Returns True if command is potentially destructive."""
        cmd_lower = command.lower().strip()
        for bad in self.destructive_commands:
            if bad in cmd_lower:
                return True
        return False

    def sanitize_text(self, text):
        """Replaces profanity with clean alternatives."""
        replacements = {
            "fuck": "freak", "fucking": "freaking",
            "shit": "stuff", "bitch": "person",
            "damn": "darn", "ass": "jerk",
            "bastard": "fool", "crap": "mess",
        }
        result = text.lower()
        for bad, good in replacements.items():
            result = re.sub(rf"\b{bad}\b", good, result, flags=re.IGNORECASE)
        return result

    def analyze_tone(self, text):
        """Detects user sentiment. Returns one of: neutral, frustrated, urgent, happy."""
        t = text.lower()
        frustrated = {"annoying", "hate", "stupid", "why", "broken", "error", "fail",
                       "not working", "useless", "damn", "slow", "fix it", "help me"}
        urgent = {"now", "immediately", "asap", "hurry", "quick", "emergency",
                   "critical", "urgent"}
        happy = {"great", "awesome", "nice", "good", "thanks", "perfect",
                  "love", "amazing", "beautiful"}

        words = set(re.sub(r"[^a-zA-Z\s]", "", t).split())

        if words & frustrated:
            return "frustrated"
        if words & urgent:
            return "urgent"
        if words & happy:
            return "happy"
        return "neutral"

    def get_empathetic_prefix(self, tone):
        """Returns a tone-aware empathetic opening."""
        prefixes = {
            "frustrated": "\n💙 I hear you — let's work through this together.",
            "urgent": "\n⚡ On it. Let's move fast and solve this.",
            "happy": "\n😊 Glad things are going well! Let's keep the momentum.",
            "neutral": "",
        }
        return prefixes.get(tone, "")

    def validate_action(self, action, user_input=""):
        """
        Full validation of an action before execution.
        Returns (is_safe, reason, sanitized_action)
        """
        payload = str(action.get("payload", ""))
        action_type = action.get("type", "")

        if action_type == "terminal":
            if self.check_destructive_command(payload):
                return False, f"Blocked by {self.name}: Destructive command detected.", action
            if self.check_hate_speech(payload):
                return False, f"Blocked by {self.name}: Hate speech detected.", action

        if action_type in ("chat_internal", "chat_unknown"):
            if self.check_profanity(payload):
                sanitized = self.sanitize_text(payload)
                action["payload"] = sanitized
                return True, "Profanity sanitized.", action
            if self.check_hate_speech(payload):
                return False, f"Blocked by {self.name}: Hate speech detected.", action

        if user_input:
            if self.check_profanity(user_input):
                return False, f"Response blocked: Please use respectful language.", action
            if self.check_hate_speech(user_input):
                return False, f"Response blocked: Hate speech is not tolerated.", action

        return True, "Approved.", action
