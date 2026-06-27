import os
import re
import json
import random
from collections import defaultdict

KNOWLEDGE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge_base.json"
)


class MarkovSynthesizer:
    def __init__(self, depth=2, max_sentences=4, min_sentences=2, min_words=10):
        self.depth = depth
        self.max_sentences = max_sentences
        self.min_sentences = min_sentences
        self.min_words = min_words
        self.chain = defaultdict(list)
        self.start_words = []
        self.total_tokens = 0
        self.sentence_enders = re.compile(r'[.!?]')

    def build(self, knowledge_file=None):
        self.chain.clear()
        self.start_words = []
        self.total_tokens = 0
        path = knowledge_file or KNOWLEDGE_FILE
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                kb = json.load(f)
        except (json.JSONDecodeError, Exception):
            return

        texts = list(kb.values())
        if not texts:
            return

        for text in texts:
            words = re.findall(r"[A-Za-z0-9'-]+|[.!?]", text.lower())
            if len(words) < self.depth + 2:
                continue
            if words:
                self.start_words.append(tuple(words[:self.depth]))
            for i in range(len(words) - self.depth):
                key = tuple(words[i:i + self.depth])
                next_word = words[i + self.depth]
                self.chain[key].append(next_word)
                self.total_tokens += 1

    def generate(self, topic=None, max_sentences=4, min_sentences=2):
        if self.total_tokens < 20:
            return None

        seed = None
        if topic:
            topic_words = re.findall(r"[A-Za-z0-9'-]+", topic.lower())
            for i in range(len(topic_words) - self.depth + 1):
                key = tuple(topic_words[i:i + self.depth])
                if key in self.chain:
                    seed = key
                    break

        if seed is None and self.start_words:
            seed = random.choice(self.start_words)

        if seed is None:
            return None

        result = list(seed)
        sentence_count = 0
        max_tokens = 80
        stale_streak = 0

        for w in result[:self.depth]:
            if self.sentence_enders.search(w):
                sentence_count += 1

        for _ in range(max_tokens):
            key = tuple(result[-self.depth:])
            if key not in self.chain:
                break
            candidates = self.chain[key]
            if not candidates:
                break
            next_word = random.choice(candidates)
            result.append(next_word)

            if self.sentence_enders.search(next_word):
                sentence_count += 1
                stale_streak = 0
            else:
                stale_streak += 1

            if sentence_count >= self.max_sentences:
                break
            if stale_streak > 15 and sentence_count >= self.min_sentences:
                break

        text = " ".join(result)
        text = re.sub(r'\s+([?.!,:])', r'\1', text)
        text = text[0].upper() + text[1:] if text else text
        sentences = self.sentence_enders.split(text)
        sentences = [s.strip() for s in sentences if s.strip()][:self.max_sentences]
        joined = ". ".join(sentences) + "." if sentences else None
        if joined and len(joined.split()) < self.min_words:
            return None
        return joined
