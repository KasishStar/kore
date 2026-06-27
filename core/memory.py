import json
import os
import time
import uuid
from datetime import datetime


class MemoryManager:
    def __init__(self, memory_dir=None, session_id=None):
        if memory_dir is None:
            memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".kore_memory")
        self.memory_dir = memory_dir
        self.session_id = session_id or uuid.uuid4().hex[:8]
        os.makedirs(self.memory_dir, exist_ok=True)

        self.working_file = os.path.join(self.memory_dir, "current.json")
        self.episodic_file = os.path.join(self.memory_dir, f"history_{self.session_id}.jsonl")
        self.global_history = os.path.join(self.memory_dir, "history.jsonl")
        self.semantic_file = os.path.join(self.memory_dir, "facts.json")

        self._init_files()

    def _init_files(self):
        if not os.path.exists(self.working_file):
            self._write_json(self.working_file, {
                "objective": None, "active_file": None,
                "last_action": None, "last_error": None,
                "cycle": 0, "status": "idle"
            })
        if not os.path.exists(self.semantic_file):
            self._write_json(self.semantic_file, {
                "user_preferences": {}, "project_facts": {}, "learned_patterns": []
            })

    def switch_session(self, session_id):
        old_file = self.episodic_file
        self.session_id = session_id
        self.episodic_file = os.path.join(self.memory_dir, f"history_{session_id}.jsonl")
        return old_file != self.episodic_file

    def _write_json(self, path, data):
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _read_json(self, path):
        with open(path, "r") as f:
            return json.load(f)

    def set_working_context(self, objective=None, active_file=None, last_action=None, last_error=None, cycle=None, status=None):
        data = self._read_json(self.working_file)
        if objective is not None: data["objective"] = objective
        if active_file is not None: data["active_file"] = active_file
        if last_action is not None: data["last_action"] = last_action
        if last_error is not None: data["last_error"] = last_error
        if cycle is not None: data["cycle"] = cycle
        if status is not None: data["status"] = status
        else: data["status"] = "active"
        data["updated_at"] = datetime.now().isoformat()
        self._write_json(self.working_file, data)

    def get_working_context(self):
        return self._read_json(self.working_file)

    def clear_working_context(self):
        self._write_json(self.working_file, {
            "objective": None, "active_file": None,
            "last_action": None, "last_error": None,
            "cycle": 0, "status": "idle",
            "updated_at": datetime.now().isoformat()
        })

    def log_event(self, event_type, summary, details=None, success=True):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "epoch": time.time(),
            "session": self.session_id,
            "type": event_type,
            "summary": summary,
            "details": details or {},
            "success": success
        }
        with open(self.episodic_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        with open(self.global_history, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_session_events(self, limit=50, event_type=None):
        if not os.path.exists(self.episodic_file):
            return []
        events = []
        with open(self.episodic_file, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        if event_type:
            events = [e for e in events if e.get("type") == event_type]
        return events[-limit:]

    def get_recent_events(self, limit=10, event_type=None):
        return self.get_session_events(limit=limit, event_type=event_type)

    def get_last_error(self):
        events = self.get_recent_events(limit=5, event_type="error")
        if events:
            return events[-1].get("summary")
        return None

    def get_error_history(self, limit=20):
        return self.get_recent_events(limit=limit, event_type="error")

    def list_sessions(self):
        sessions = set()
        if not os.path.exists(self.global_history):
            return []
        with open(self.global_history, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        e = json.loads(line)
                        s = e.get("session", "")
                        if s and len(s) == 8:
                            sessions.add(s)
                    except json.JSONDecodeError:
                        continue
        return sorted(sessions)

    def clear_session(self):
        if os.path.exists(self.episodic_file):
            os.remove(self.episodic_file)
        self.clear_working_context()

    def clear_all_sessions(self):
        for f in os.listdir(self.memory_dir):
            if f.startswith("history_") and f.endswith(".jsonl"):
                os.remove(os.path.join(self.memory_dir, f))
        if os.path.exists(self.global_history):
            os.remove(self.global_history)
        self.clear_working_context()

    def learn_fact(self, category, key, value):
        data = self._read_json(self.semantic_file)
        if category not in data:
            data[category] = {}
        data[category][key] = {"value": value, "learned_at": datetime.now().isoformat()}
        self._write_json(self.semantic_file, data)
        self.log_event("learn", f"Learned: {category}.{key} = {value}")

    def get_fact(self, category, key=None):
        data = self._read_json(self.semantic_file)
        if category not in data:
            return None
        if key is None:
            return data[category]
        return data[category].get(key)

    def get_all_facts(self):
        return self._read_json(self.semantic_file)

    def learn_pattern(self, pattern, context, success=True):
        data = self._read_json(self.semantic_file)
        data["learned_patterns"].append({
            "pattern": pattern, "context": context,
            "success": success, "learned_at": datetime.now().isoformat()
        })
        self._write_json(self.semantic_file, data)

    def get_similar_pattern(self, context):
        data = self._read_json(self.semantic_file)
        patterns = data.get("learned_patterns", [])
        context_lower = context.lower()
        for p in reversed(patterns):
            if p["context"].lower() in context_lower or context_lower in p["context"].lower():
                return p
        return None

    def build_context_prompt(self, user_input):
        working = self.get_working_context()
        recent = self.get_recent_events(limit=5)
        facts = self.get_all_facts()
        lines = []
        lines.append("=== WORKING CONTEXT ===")
        if working.get("objective"):
            lines.append(f"  Current Objective: {working['objective']}")
        if working.get("active_file"):
            lines.append(f"  Active File: {working['active_file']}")
        if working.get("last_error"):
            lines.append(f"  Last Error: {working['last_error']}")
        lines.append("\n=== RECENT HISTORY ===")
        for e in recent[-3:]:
            status = "✓" if e.get("success") else "✗"
            lines.append(f"  [{status}] {e.get('type','?')}: {e.get('summary','')}")
        pref = facts.get("user_preferences", {})
        if pref:
            lines.append("\n=== USER PREFERENCES ===")
            for k, v in pref.items():
                val = v.get("value", v) if isinstance(v, dict) else v
                lines.append(f"  • {k}: {val}")
        proj = facts.get("project_facts", {})
        if proj:
            lines.append("\n=== PROJECT FACTS ===")
            for k, v in proj.items():
                val = v.get("value", v) if isinstance(v, dict) else v
                lines.append(f"  • {k}: {val}")
        lines.append(f"\n=== NEW INPUT ===")
        lines.append(f"  {user_input}")
        return "\n".join(lines)
