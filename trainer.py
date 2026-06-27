#!/usr/bin/env python3
"""
Kore Self-Training Manager
Monitors error events and autonomously expands Kore's knowledge domain.
Zero external dependencies — Python stdlib only.
"""

import json
import os
import re
import time
import shutil
import ast
from datetime import datetime
try:
    from core.websearch import WebReflex
except ImportError:
    WebReflex = None


BASE = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE, ".kore_memory")
HISTORY_FILE = os.path.join(MEMORY_DIR, "history.jsonl")
PATCH_DIR = os.path.join(BASE, "patches")
LOG_FILE = os.path.join(BASE, "trainer.log")
KNOWLEDGE_FILE = os.path.join(BASE, "knowledge_base.json")
CONFIG_FILE = os.path.join(BASE, "config.json")

CONFIG = {}
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, "r") as f:
            CONFIG = json.load(f)
    except (json.JSONDecodeError, Exception):
        pass

POLL_INTERVAL = CONFIG.get("trainer", {}).get("poll_interval_seconds", 30)
MAX_PATCH_WORDS = CONFIG.get("trainer", {}).get("max_patch_words", 500)


def log(msg):
    ts = datetime.now().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def read_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    events = []
    with open(HISTORY_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def get_unseen_errors(seen_count):
    events = read_history()
    new_errors = []
    for e in events[seen_count:]:
        if e.get("type") in ("error", "chat_unknown", "exec_error", "cmd_error"):
            new_errors.append(e)
    return new_errors, len(events)


STOPWORDS = {
    "what", "when", "where", "why", "how", "which", "who", "whom",
    "this", "that", "these", "those", "the", "a", "an", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "can", "could", "shall",
    "should", "may", "might", "must", "not", "no", "nor", "none",
    "and", "or", "but", "if", "then", "else", "so", "than", "too",
    "very", "just", "about", "also", "its", "it's", "im", "i'm",
    "you", "your", "me", "my", "we", "our", "they", "their", "he",
    "she", "his", "her", "him", "all", "any", "each", "every",
    "some", "both", "few", "more", "most", "other", "into", "upon",
    "with", "for", "from", "to", "in", "on", "at", "by", "up", "out",
    "off", "over", "after", "before", "between", "through", "during",
    "tell", "show", "give", "make", "get", "set", "put", "take",
    "let", "ask", "need", "want", "like", "use", "try", "know",
    "think", "see", "look", "find", "call", "come", "go", "say",
}


def extract_keywords(text):
    words = set(re.sub(r"[^a-zA-Z\s]", "", text.lower()).split())
    return {w for w in words if len(w) > 3 and w not in STOPWORDS}


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def write_file_atomic(path, content):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(content)
    os.replace(tmp, path)


def backup_file(path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = f"{path}.{ts}.bak"
    shutil.copy2(path, backup)
    return backup


def append_to_vector(vector_str, new_words):
    existing = set(vector_str.split())
    added = [w for w in new_words if w not in existing]
    if not added:
        return vector_str, []
    return vector_str + " " + " ".join(added), added


MAX_VECTOR_WORDS = MAX_PATCH_WORDS


def patch_education_vector(new_keywords):
    path = os.path.join(BASE, "core", "reflexes.py")
    content = read_file(path)
    m = re.search(r'"education"\s*:\s*"([^"]+)"', content)
    if not m:
        log("  ERROR: education vector not found in reflexes.py")
        return False
    old_vec = m.group(1)
    if len(old_vec.split()) >= MAX_VECTOR_WORDS:
        log(f"  WARNING: education vector at {len(old_vec.split())} words (max {MAX_VECTOR_WORDS}). Skipping.")
        return False
    new_vec, added = append_to_vector(old_vec, new_keywords)
    if not added:
        log("  No new keywords to add (all already present)")
        return True
    backup_file(path)
    old_str = f'"{old_vec}"'
    new_str = f'"{new_vec}"'
    content = content.replace(old_str, new_str, 1)
    try:
        ast.parse(content)
    except SyntaxError:
        log(f"  ERROR: Patch would cause syntax error — aborting")
        return False
    write_file_atomic(path, content)
    log(f"  Expanded education vector with: {', '.join(sorted(added))}")
    return True


def patch_study_words(new_keywords):
    path = os.path.join(BASE, "core", "persona.py")
    content = read_file(path)
    m = re.search(r'study_words\s*=\s*\{([^}]+)\}', content)
    if not m:
        log("  ERROR: study_words set not found in persona.py")
        return False
    existing = set(re.findall(r'"([^"]+)"', m.group(1)))
    added = {w for w in new_keywords if w not in existing}
    if not added:
        log("  No new study words to add (all already present)")
        return True
    new_set = existing | added
    new_block = "study_words = {" + ", ".join(f'"{w}"' for w in sorted(new_set)) + "}"
    backup_file(path)
    content = content.replace(m.group(0), new_block, 1)
    try:
        ast.parse(content)
    except SyntaxError:
        log(f"  ERROR: Patch would cause syntax error in persona.py — aborting")
        return False
    write_file_atomic(path, content)
    log(f"  Expanded study_words with: {', '.join(sorted(added))}")
    return True


def patch_edu_words(new_keywords):
    path = os.path.join(BASE, "core", "persona.py")
    content = read_file(path)
    for name in ["edu_words", "study_words"]:
        m = re.search(rf'{name}\s*=\s*{{([^}}]+)}}', content)
        if m:
            existing = set(re.findall(r'"([^"]+)"', m.group(1)))
            added = {w for w in new_keywords if w not in existing}
            if added:
                new_set = existing | added
                new_block = f'{name} = {{' + ", ".join(f'"{w}"' for w in sorted(new_set)) + "}"
                backup_file(path)
                content = content.replace(m.group(0), new_block, 1)
                try:
                    ast.parse(content)
                except SyntaxError:
                    log(f"  ERROR: Syntax error patching {name} — aborting")
                    return False
                write_file_atomic(path, content)
                log(f"  Expanded {name} with: {', '.join(sorted(added))}")
    return True


def log_patch(input_text, error_msg, module, keywords_added):
    os.makedirs(PATCH_DIR, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": input_text,
        "error": error_msg,
        "module": module,
        "keywords_added": list(keywords_added),
    }
    patch_log = os.path.join(PATCH_DIR, "log.json")
    patches = []
    if os.path.exists(patch_log):
        with open(patch_log, "r") as f:
            try:
                patches = json.load(f)
            except json.JSONDecodeError:
                patches = []
    patches.append(entry)
    write_file_atomic(patch_log, json.dumps(patches, indent=2))
    log(f"  Logged patch #{len(patches)} to patches/log.json")


def clean_input(text):
    for prefix in ["Responded to: ", "Searched: ", "Running: ", "Writing: ", "Learned: "]:
        if text.startswith(prefix):
            text = text[len(prefix):]
    return text


def load_knowledge():
    if not os.path.exists(KNOWLEDGE_FILE):
        return {}
    try:
        with open(KNOWLEDGE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}


def save_knowledge(kb):
    atomic_dir = os.path.dirname(KNOWLEDGE_FILE)
    tmp = KNOWLEDGE_FILE + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(kb, f, indent=2)
        os.replace(tmp, KNOWLEDGE_FILE)
    except Exception as e:
        log(f"  ERROR saving knowledge base: {e}")


def summarize_snippets(snippets, max_sentences=3):
    text = " ".join(s.strip() for s in snippets if s.strip())
    if not text:
        return ""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    result = []
    for s in sentences:
        s = s.strip()
        if len(s) < 15:
            continue
        result.append(s)
        if len(result) >= max_sentences:
            break
    return " ".join(result)


def cache_concept(concept, summary):
    kb = load_knowledge()
    if concept in kb:
        return False
    kb[concept] = summary
    save_knowledge(kb)
    log(f"  Cached knowledge: {concept}")
    return True


def process_errors(errors):
    total = 0
    for err in errors:
        etype = err.get("type", "")
        if etype != "chat_unknown":
            continue

        summary = err.get("summary", "")
        details = err.get("details", "")
        input_text = clean_input(summary or str(details))
        keywords = extract_keywords(input_text)

        if not keywords:
            log(f"  No meaningful keywords in: {input_text[:60]}")
            continue

        log(f"  Processing: {input_text[:60]}...")
        log(f"  Extracted keywords: {', '.join(sorted(keywords))}")

        if patch_education_vector(keywords):
            patch_study_words(keywords)
            patch_edu_words(keywords)
            log_patch(input_text, str(details) if details else summary, "education", keywords)
            total += 1
            log(f"  Learned {len(keywords)} new terms from this error")

        concept = " ".join(sorted(keywords))[:120]
        kb = load_knowledge()
        if concept not in kb and WebReflex is not None:
            log(f"  Searching web for: {input_text[:50]}...")
            try:
                w = WebReflex()
                results = w.search(input_text, max_results=3)
                snippets = [r.get("snippet", "") for r in results if r.get("snippet")]
                if not snippets:
                    snippets = [r.get("title", "") for r in results]
                summary_text = summarize_snippets(snippets)
                if summary_text:
                    cache_concept(concept, summary_text)
                else:
                    log(f"  No summary generated from search results")
            except Exception as e:
                log(f"  Web search failed: {e}")
    return total


def train():
    log("Kore Self-Training Manager starting")
    log(f"Watching: {HISTORY_FILE}")
    os.makedirs(PATCH_DIR, exist_ok=True)
    processed_file = os.path.join(PATCH_DIR, "processed_count.txt")

    last_processed = 0
    if os.path.exists(processed_file):
        with open(processed_file, "r") as f:
            try: last_processed = int(f.read().strip())
            except: last_processed = 0

    total_patches = 0

    while True:
        try:
            events = read_history()
            if len(events) > last_processed:
                new_errors = [e for e in events[last_processed:]
                              if e.get("type") in ("error", "chat_unknown", "exec_error", "cmd_error")]
                if new_errors:
                    log(f"Found {len(new_errors)} new error(s) to learn from")
                    total_patches += process_errors(new_errors)
                    log(f"Training cycle complete. Total patches: {total_patches}")
                last_processed = len(events)
                with open(processed_file, "w") as f:
                    f.write(str(last_processed))
        except KeyboardInterrupt:
            log(f"Shutdown. Total patches applied: {total_patches}")
            break
        except Exception as e:
            log(f"ERROR in training loop: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    train()
