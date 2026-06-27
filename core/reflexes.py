import os
import math
import random
import re
import urllib.parse

class InfantReflexes:
    def __init__(self):
        self.sensory_matrix = {}
        self.sandbox_file = "kore_sandbox.py"

        self.action_verbs = {
            "ls","ps","top","free","list","search","status","ping","ip",
            "run","execute","display","read","open","create","write",
            "make","build","generate","move","copy",
            "sort","count","sum","calculate","show","find","check"
        }
        self.web_phrases = {
            "search for","search the web","latest news","meaning of",
            "information about","tell me about","how to","what does"
        }

        self.internal_domain_vectors = {
            "identity_purpose": "kore identity purpose created architecture autonomous reflex agent zero-knowledge local companion mission design",
            "system_operation": "files folders processes ram memory storage cpu network linux hardware terminal automation command shell",
            "coding_help": "code script program function class algorithm debug fix error generate python fibonacci",
            "education": "math maths science physics chemistry biology solve solving calculate calculator equation formula newton newtons theorem algebra geometry exam exams homework study studies studying learn learning school class photosynthesis force energy motion speed velocity acceleration gravity explain explanation define definition best movie",
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
            "list_dir": (
                "import os\n"
                "for f in os.listdir('.'):\n"
                "    size = os.path.getsize(f) if os.path.isfile(f) else 0\n"
                "    print(f'{f:30} {size:>8} bytes')\n"
            ),
            "system_info": (
                "import platform\n"
                "import os\n"
                "print(f'System: {platform.uname()}')\n"
                "with open('/proc/meminfo') as f:\n"
                "    for line in f:\n"
                "        if 'MemTotal' in line or 'MemAvailable' in line:\n"
                "            print(line.strip())\n"
                "print(f'CPU Cores: {os.cpu_count()}')\n"
                "print(f'User: {os.getlogin()}')\n"
            ),
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
        o = objective.lower()
        w = set(o.split())
        url_pattern = re.compile(r'https?://[^\s]+')
        if url_pattern.search(objective):
            return "fetch_url"
        identity_q = {"who are you","what are you","how are you","you doing",
                      "what is your purpose","why were you created"}
        if any(p in o for p in identity_q): return "chat"
        if w & {"search","lookup","google","define","meaning","current","latest","weather","searh"}:
            return "web_search"
        if any(p in o for p in self.web_phrases): return "web_search"
        code_words = {"python","code","script","function","class","program",
                      "write","generate","create","build","implement"}
        if w & code_words:
            return "code_generation"
        if "system info" in o or "system status" in o: return "code_generation"
        if w & self.action_verbs: return "terminal"
        if re.search(r'what\s+is\s+\d+\s*[+\-*/]', o) or re.search(r'^what\s+is\s+\d+$', o): return "code_generation"
        return "chat"

    def _code_area(self, obj):
        shapes = {
            "circle": (["r"], "math.pi * r ** 2", True),
            "rectangle": (["l", "w"], "l * w", False),
            "square": (["s"], "s ** 2", False),
            "triangle": (["b", "h"], "0.5 * b * h", False),
        }
        for name, (vars, formula, needs_math) in shapes.items():
            if name in obj:
                import_line = "import math\n" if needs_math else ""
                prompts = "\n".join(f"    {v} = float(input('{v}: '))" for v in vars)
                return (f"{import_line}def area():\n{prompts}\n"
                        f"    result = {formula}\n"
                        f"    print(f'Area: {{result}}')\narea()\n")
        return None

    def generate_code_draft(self, objective):
        obj = objective.lower()
        if "fibonacci" in obj: return self.code_blueprints["fibonacci"]
        if "hardware" in obj or "spec" in obj: return self.code_blueprints["hardware"]
        if "list" in obj or "dir" in obj or "files" in obj: return self.code_blueprints["list_dir"]
        if "system" in obj and ("info" in obj or "status" in obj): return self.code_blueprints["system_info"]
        if ("area" in obj or "calculate" in obj) and self._code_area(obj): return self._code_area(obj)
        if "factorial" in obj:
            m = re.search(r'\d+', obj)
            n = m.group() if m else "10"
            return (f"def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)\n"
                    f"print(f'{n}! = {{factorial({n})}}')\n")
        if "prime" in obj:
            m = re.search(r'\d+', obj)
            limit = m.group() if m else "50"
            return (f"def is_prime(n):\n    if n < 2: return False\n"
                    f"    for i in range(2, int(n**0.5)+1):\n"
                    f"        if n % i == 0: return False\n    return True\n"
                    f"primes = [n for n in range(2, {limit}+1) if is_prime(n)]\n"
                    f"print(f'Primes up to {limit}: {{primes}}')\n")
        if "sort" in obj:
            return ("items = input('Enter numbers: ').split()\nnums = [int(x) for x in items]\n"
                    "nums.sort()\nprint(f'Sorted: {nums}')\nprint(f'Reversed: {list(reversed(nums))}')\n")
        if "reverse" in obj and ("string" in obj or "text" in obj):
            return ("text = input('Enter text: ')\nprint(f'Reversed: {text[::-1]}')\n"
                    "print(f'Palindrome: {text == text[::-1]}')\n")
        if "count" in obj and ("word" in obj):
            return ("text = input('Enter text: ')\nwords = text.split()\n"
                    "print(f'Words: {len(words)}')\nprint(f'Chars: {len(text)}')\n"
                    "print(f'Unique: {len(set(w.lower() for w in words))}')\n")
        if "table" in obj or "multiplication" in obj:
            return ("n = int(input('Enter a number: '))\n"
                    "for i in range(1, 11):\n    print(f\"{n} x {i} = {n*i}\")\n")
        m = re.search(r'what\s+is\s+([\d\s+\-*/()]+)', obj)
        if m:
            expr = m.group(1).strip()
            return f"print({expr})\n"
        return ("import os\nimport platform\n"
                "print('Kore Generated Script')\n"
                "print(f'Platform: {platform.system()} {platform.release()}')\n"
                "print(f'Python: {platform.python_version()}')\n"
                "print(f'CWD: {os.getcwd()}')\n"
                "files = os.listdir('.')\nprint(f'Files: {len(files)}')\n")

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
        obj = context["objective"]
        intent = self.analyze_intent(obj)

        if intent == "chat":
            obj_lower = obj.lower().strip().rstrip("?!.")
            if obj_lower in {"hi","hello","hey","yo","sup","howdy"}:
                return [{"type": "chat_internal", "payload": obj, "rank": 1}]
            if any(p in obj_lower for p in ["who are you","what are you","how are you","you doing"]):
                return [{"type": "chat_internal", "payload": obj, "rank": 1}]
            scores = {k: self.calculate_semantic_closeness(obj, self.internal_domain_vectors[k])
                      for k in self.internal_domain_vectors}
            if max(scores.values()) >= 0.1:
                return [{"type": "chat_internal", "payload": obj, "rank": 1}]
            ow = set(obj.lower().split())
            dv_all = " ".join(self.internal_domain_vectors.values())
            if any(w in dv_all for w in ow if len(w) > 3):
                return [{"type": "chat_internal", "payload": obj, "rank": 1}]
            return [{"type": "chat_unknown", "payload": obj, "rank": 1}]

        if intent == "code_generation":
            code = self.generate_code_draft(obj)
            if failure_log: code = self._mutate_code(code, failure_log)
            return [{"type": "execute_code", "payload": code, "file": self.sandbox_file, "rank": 1}]

        if intent == "web_search":
            return [{"type": "web_search", "payload": obj, "rank": 1}]

        if intent == "fetch_url":
            url_pattern = re.compile(r'https?://[^\s]+')
            m = url_pattern.search(objective)
            url = m.group(0) if m else obj
            return [{"type": "fetch_url", "payload": url, "rank": 1}]

        scores = {k: self.calculate_semantic_closeness(obj, k) for k in self.motor_skills}
        best = max(scores, key=scores.get)
        ow = obj.lower().split()
        if "whole system" in obj.lower() or "everywhere" in obj.lower(): best = "system_search"
        elif "ram" in ow or "memory" in ow or "cpu" in ow: best = "system_monitor"
        elif "net" in ow or "ping" in ow or "ip" in ow: best = "network_status"
        elif scores[best] == 0.0: best = "file_io"

        hypotheses = []
        for idx, payload in enumerate(self.motor_skills[best]):
            actual = payload
            if failure_log:
                if "permission" in failure_log.lower() or "denied" in failure_log.lower():
                    actual = f"sudo {actual}" if "sudo" not in actual else actual
                else: actual = f"{actual} # adaptive_retry"
            hypotheses.append({"type": "terminal", "payload": actual, "rank": idx})
        return hypotheses
