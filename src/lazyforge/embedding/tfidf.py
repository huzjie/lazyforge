"""tfidf —— TF-IDF 向量化（零依赖稀疏表示）。

`fit_transform` 从语料学习 IDF，`transform` 对新文本得到加权稀疏向量。
向量以 dict 存储（term -> weight），检索阶段做点积 / 余弦，避免稠密矩阵
的内存开销 —— 对「数百个工具 stub」这种规模足够快、足够省。
"""
from __future__ import annotations

import math
from collections import Counter
from typing import Iterable

from .tokenizer import tokenize


class TfidfVectorizer:
    def __init__(
        self,
        ngram_range: tuple[int, int] = (1, 2),
        min_df: int = 1,
        idf_smoothing: float = 0.5,
    ) -> None:
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.idf_smoothing = idf_smoothing
        self._df: dict[str, int] = Counter()
        self._n_docs = 0
        self._idf: dict[str, float] = {}

    def _tokens(self, text: str) -> list[str]:
        return tokenize(text, self.ngram_range)

    def fit(self, documents: Iterable[str]) -> "TfidfVectorizer":
        docs = list(documents)
        self._n_docs = len(docs)
        df: Counter[str] = Counter()
        for doc in docs:
            for term in set(self._tokens(doc)):
                df[term] += 1
        self._df = df
        # 平滑 IDF：idf = log((N+1)/(df+smoothing)) + 1
        n = self._n_docs
        self._idf = {
            term: math.log((n + 1) / (cnt + self.idf_smoothing)) + 1
            for term, cnt in df.items()
            if cnt >= self.min_df
        }
        return self

    def transform(self, text: str) -> dict[str, float]:
        """得到 dict: term -> tf-idf 权重（未归一化）。"""
        if self._n_docs == 0:
            return {}
        counts = Counter(self._tokens(text))
        total = sum(counts.values()) or 1
        out: dict[str, float] = {}
        for term, cnt in counts.items():
            idf = self._idf.get(term, 0.0)
            if idf:
                out[term] = (cnt / total) * idf
        return out

    def fit_transform(self, documents: Iterable[str]) -> list[dict[str, float]]:
        docs = list(documents)
        self.fit(docs)
        return [self.transform(d) for d in docs]
