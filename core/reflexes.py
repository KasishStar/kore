import os
import math
import random

class InfantReflexes:
    def __init__(self):
        self.sensory_matrix = {}
        self.sandbox_file = "kore_sandbox.py"

        self.action_verbs = {
            "check", "show", "find", "ls", "ps", "top", "free", "list",
            "search", "status", "ping", "ip", "run", "execute", "display",
            "read", "open", "create", "write", "make", "build", "generate",
            "compile", "install", "remove", "delete", "move", "copy",
            "sort", "count", "sum", "calculate", "compute"
        }

        self.internal_domain_vectors = {
            "identity_purpose": "kore identity purpose created architecture autonomous reflex agent zero-knowledge local companion mission design",
            "system_operation": "files folders processes ram memory storage cpu network linux hardware terminal automation command shell",
            "coding_help": "code script program function class algorithm debug fix error generate python fibonacci"
        }

        self.motor_skills = {
            "system_monitor": [
                "ps aux --sort=-%cpu | head -n 5",
                "top -b -n 1 | head -n 10",
                "free -m"
            ],
            "file_io": [
                "find . -maxdepth 2 -type f",
                "ls -la",
                "du -sh *"
            ],
            "network_status": [
                "ip a",
                "ping -c 3 google.com",
                "ss -tulpn"
            ],
            "system_search": [
                "find / -name '*python*' -type f 2>/dev/null | head -n 20",
                "whereis python"
            ]
        }

        self.code_blueprints = {
            "fibonacci": (
                "def fib(n):\n"
                "    return n if n <= 1 else fib(n-1) + fib(n-2)\n"
                "print([fib(i) for i in range(10)])\n"
            ),
            "hardware": (
                "import platform\n"
                "import os\n"
                "print(f'OS: {platform.system()} {platform.release()}')\n"
                "print(f'CPU Cores: {os.cpu_count()}')\n"
                "print(f'User: {os.getlogin()}')\n"
            ),
            "hello": (
                "print('Hello from the Kore autonomous engine!')\n"
            ),
            "list_dir": (
                "import os\n"
                "for f in os.listdir('.'):\n"
                "    size = os.path.getsize(f) if os.path.isfile(f) else 0\n"
                "    print(f'{f:30} {size:>8} bytes')\n"
            ),
            "system_info": (
                "import platform\n"
                "import psutil\n"
                "print(f'System: {platform.uname()}')\n"
                "print(f'RAM: {psutil.virtual_memory().total / 1e9:.2f} GB total, '\n"
                "      f'{psutil.virtual_memory().available / 1e9:.2f} GB available')\n"
                "print(f'CPU: {psutil.cpu_percent(interval=1)}% used')\n"
            )
        }

    def _get_word_vector(self, text):
        words = text.lower().split()
        counts = {}
        for w in words:
            w = w.strip(",.!?;:'\"()[]{}")
            if w:
                counts[w] = counts.get(w, 0) + 1
        magnitude = math.sqrt(sum(v ** 2 for v in counts.values()))
        return counts, magnitude

    def calculate_semantic_closeness(self, text_a, text_b):
        vec_a, mag_a = self._get_word_vector(text_a)
        vec_b, mag_b = self._get_word_vector(text_b)
        if mag_a == 0 or mag_b == 0:
            return 0.0
        dot_product = sum(
            vec_a[w] * vec_b.get(w, 0) for w in vec_a if w in vec_b
        )
        return dot_product / (mag_a * mag_b)

    def ingest_environment(self, objective):
        self.sensory_matrix = {
            "objective": objective.strip(),
            "pwd": os.getcwd(),
            "user": os.environ.get("USER", "user"),
            "os": os.name
        }
        return self.sensory_matrix

    def analyze_intent(self, objective):
        words = set(objective.lower().split())
        code_keywords = {"python", "code", "script", "function", "class", "program",
                         "write", "generate", "create", "build", "implement"}
        if words.intersection(code_keywords):
            return "code_generation"
        if words.intersection(self.action_verbs):
            return "terminal"
        return "chat"

    def generate_code_draft(self, objective):
        obj = objective.lower()
        if "fibonacci" in obj:
            return self.code_blueprints["fibonacci"]
        if "hardware" in obj or "spec" in obj:
            return self.code_blueprints["hardware"]
        if "list" in obj or "dir" in obj or "files" in obj:
            return self.code_blueprints["list_dir"]
        if "system" in obj and ("info" in obj or "status" in obj):
            return self.code_blueprints["system_info"]
        return self.code_blueprints["hello"]

    def _mutate_code(self, code, error_log):
        mutated = "# Kore Self-Correction Applied\n"
        mutated += f"# Error received: {error_log[:80]}\n"
        mutated += (
            "import platform\n"
            "import os\n"
            "try:\n"
            f"    {code.replace(chr(10), chr(10)+'    ')}\n"
            "except Exception as e:\n"
            "    print(f'Kore caught: {e}')\n"
            "    print(f'Platform: {platform.uname()}')\n"
        )
        return mutated

    def mutate_hypotheses(self, context, failure_log=None):
        objective = context["objective"]
        intent = self.analyze_intent(objective)

        if intent == "chat":
            obj_lower = objective.lower().strip().rstrip("?!.")
            greeting_words = {"hi", "hello", "hey", "yo", "sup", "howdy"}
            identity_phrases = ["who are you", "what are you", "how are you", "you doing"]
            if obj_lower in greeting_words:
                return [{"type": "chat_internal", "payload": objective, "rank": 1}]
            if any(p in obj_lower for p in identity_phrases):
                return [{"type": "chat_internal", "payload": objective, "rank": 1}]
            identity_score = self.calculate_semantic_closeness(
                objective, self.internal_domain_vectors["identity_purpose"]
            )
            system_score = self.calculate_semantic_closeness(
                objective, self.internal_domain_vectors["system_operation"]
            )
            coding_score = self.calculate_semantic_closeness(
                objective, self.internal_domain_vectors["coding_help"]
            )
            max_score = max(identity_score, system_score, coding_score)
            if max_score < 0.1:
                return [{"type": "chat_unknown", "payload": objective, "rank": 1}]
            return [{"type": "chat_internal", "payload": objective, "rank": 1}]

        if intent == "code_generation":
            if failure_log:
                code = self.generate_code_draft(objective)
                return [{
                    "type": "execute_code",
                    "payload": self._mutate_code(code, failure_log),
                    "file": self.sandbox_file,
                    "rank": 1
                }]
            initial_code = self.generate_code_draft(objective)
            return [{
                "type": "execute_code",
                "payload": initial_code,
                "file": self.sandbox_file,
                "rank": 1
            }]

        scores = {
            k: self.calculate_semantic_closeness(objective, k)
            for k in self.motor_skills
        }
        best_cluster = max(scores, key=scores.get)

        if "whole system" in objective.lower() or "everywhere" in objective.lower():
            best_cluster = "system_search"
        elif "ram" in objective.lower() or "memory" in objective.lower() or "cpu" in objective.lower():
            best_cluster = "system_monitor"
        elif "net" in objective.lower() or "ping" in objective.lower() or "ip" in objective.lower():
            best_cluster = "network_status"
        elif scores[best_cluster] == 0.0:
            best_cluster = "file_io"

        raw_options = self.motor_skills[best_cluster]
        hypotheses = []
        for idx, payload in enumerate(raw_options):
            actual = payload
            if failure_log:
                if "permission" in failure_log.lower() or "denied" in failure_log.lower():
                    if "sudo" not in actual:
                        actual = f"sudo {actual}"
                else:
                    actual = f"{actual} # adaptive_retry"
            hypotheses.append({"type": "terminal", "payload": actual, "rank": idx})
        return hypotheses
