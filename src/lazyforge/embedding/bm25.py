"""bm25 —— 稀疏检索的经典强基线。

BM25 对「工具名 + 摘要」这类短文本尤其好用：query 里的稀有词权重更高，
命中率对「找对工具」这个目标非常关键。零依赖实现，用于 sparse 后端。
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

from .tokenizer import tokenize


class BM25:
    def __init__(self, k1: float = 1.5, b: float = 0.75, ngram_range: tuple[int, int] = (1, 2)):
        self.k1 = k1
        self.b = b
        self.ngram_range = ngram_range
        self._docs: list[Counter[str]] = []
        self._doc_len: list[int] = []
        self._avgdl = 0.0
        self._df: Counter[str] = Counter()
        self._n_docs = 0

    def _tokens(self, text: str) -> list[str]:
        return tokenize(text, self.ngram_range)

    def index(self, documents: Iterable[str]) -> "BM25":
        docs = list(documents)
        self._n_docs = len(docs)
        for doc in docs:
            toks = self._tokens(doc)
            self._docs.append(Counter(toks))
            self._doc_len.append(len(toks))
            for term in set(toks):
                self._df[term] += 1
        self._avgdl = sum(self._doc_len) / max(1, self._n_docs)
        return self

    def _idf(self, term: str) -> float:
        df = self._df.get(term, 0)
        return math.log((self._n_docs - df + 0.5) / (df + 0.5) + 1.0)

    def score(self, query: str, doc_idx: int) -> float:
        q = self._tokens(query)
        if not q:
            return 0.0
        doc = self._docs[doc_idx]
        dl = self._doc_len[doc_idx]
        score = 0.0
        for term in set(q):
            tf = doc.get(term, 0)
            if not tf:
                continue
            idf = self._idf(term)
            denom = tf + self.k1 * (1 - self.b + self.b * dl / max(1.0, self._avgdl))
            score += idf * (tf * (self.k1 + 1)) / denom
        return score

    def scores(self, query: str) -> list[float]:
        return [self.score(query, i) for i in range(self._n_docs)]
