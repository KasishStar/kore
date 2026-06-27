"""
IncrementalLearner — Lightweight TF-IDF model for Kore.
No numpy, no scikit-learn. Pure Python statistical learning.
"""

import os
import re
import math
import json
from collections import Counter, defaultdict

KNOWLEDGE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "knowledge_base.json"
)


class IncrementalLearner:
    def __init__(self):
        self.documents = {}
        self.idf = {}
        self.doc_vectors = {}
        self.vocabulary = set()
        self.total_docs = 0
        self.fitted = False

    def fit(self, knowledge_base=None):
        if knowledge_base is None:
            kb = self._load_kb()
        else:
            kb = knowledge_base
        self.documents = dict(kb)
        self.total_docs = len(self.documents)
        if self.total_docs == 0:
            self.fitted = False
            return
        self.vocabulary = set()
        doc_freq = defaultdict(int)
        for concept, text in self.documents.items():
            words = self._tokenize(text + " " + concept)
            unique = set(words)
            self.vocabulary.update(unique)
            for w in unique:
                doc_freq[w] += 1
        self.idf = {}
        for word in self.vocabulary:
            self.idf[word] = math.log((self.total_docs + 1) / (doc_freq[word] + 1)) + 1
        self.doc_vectors = {}
        for concept, text in self.documents.items():
            self.doc_vectors[concept] = self._vectorize(text + " " + concept)
        self.fitted = True

    def _load_kb(self):
        path = KNOWLEDGE_FILE
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}

    def _tokenize(self, text):
        return re.findall(r"[a-z0-9']+", text.lower())

    def _vectorize(self, text):
        words = self._tokenize(text)
        tf = Counter(words)
        total = len(words) or 1
        vec = {}
        for word, count in tf.items():
            if word in self.idf:
                vec[word] = (count / total) * self.idf[word]
        return vec

    def _cosine_similarity(self, vec_a, vec_b):
        intersection = set(vec_a.keys()) & set(vec_b.keys())
        dot = sum(vec_a[w] * vec_b[w] for w in intersection)
        mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
        mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)

    def predict(self, query, threshold=0.08):
        if not self.fitted or not self.doc_vectors:
            return None
        q_vec = self._vectorize(query)
        best_score = 0.0
        best_match = None
        for concept, doc_vec in self.doc_vectors.items():
            score = self._cosine_similarity(q_vec, doc_vec)
            if score > best_score:
                best_score = score
                best_match = concept
        if best_score >= threshold and best_match:
            return self.documents[best_match]
        return None

    def add_document(self, concept, text):
        self.documents[concept] = text
        self.fit(self.documents)
