class SaabValidator:
    def __init__(self):
        self.forbidden_patterns = [
            "rm -rf /",
            "rm -rf /*",
            "mkfs",
            ":(){ :|:& };:",
            "dd if=",
            "> /dev/sda",
            "> /dev/nvme",
            "chmod 777 /",
            "chmod -R 777",
            "mv / /dev/null",
            "wget -O- | sh",
            "curl -sSL | sh",
            "curl https:// | bash",
            "poweroff",
            "shutdown -h now",
            "reboot"
        ]

    def is_safe_command(self, payload):
        payload_lower = payload.lower().strip()
        for pattern in self.forbidden_patterns:
            if pattern in payload_lower:
                return False
        return True

    def process_supervision(self, hypotheses):
        scored = []
        for h in hypotheses:
            score = 1.0
            payload = str(h.get("payload", ""))

            if not self.is_safe_command(payload):
                score = 0.0

            if "sudo" in payload:
                score *= 0.5

            if h.get("type") in ("chat_internal", "chat_unknown"):
                score = 1.0

            if h.get("type") == "execute_code":
                score = 1.0

            if h.get("type") == "web_search":
                score = 1.0

            scored.append((score, h))

        scored.sort(key=lambda x: x[0], reverse=True)

        if scored and scored[0][0] == 0.0:
            return {"type": "safe_halt", "payload": "All options blocked by safety validator.", "rank": -1}

        return scored[0][1]
