"""index —— 工具索引：把 registry 的 stub 集合建成可检索的稀疏向量库。

同时维护三套表示：
- tfidf：稠密-ish 稀疏向量（词项 -> TF-IDF 权重），dense 后端
- bm25：经典稀疏检索，sparse 后端
- hashed：特征哈希向量（无词典），供 hybrid 兜底 / 快速匹配
三者零依赖，`build()` 一次 fit，`dense_scores` / `sparse_scores` 即时打分。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from ..embedding import BM25, HashedVectorizer, TfidfVectorizer, cosine, dot
from ..registry.tool import ToolStub


@dataclass
class ToolIndex:
    """工具语义索引。stubs 与三套向量化器保持一一对应。"""
    stubs: list[ToolStub] = field(default_factory=list)
    _texts: list[str] = field(default_factory=list)
    _tfidf: TfidfVectorizer | None = None
    _dense_vectors: list[dict[str, float]] = field(default_factory=list)
    _bm25: BM25 | None = None
    _hasher: HashedVectorizer | None = None
    _hash_vectors: list[dict[int, float]] = field(default_factory=list)

    @classmethod
    def from_stubs(
        cls,
        stubs: Iterable[ToolStub],
        hash_dim: int = 2048,
        ngram_range: tuple[int, int] = (1, 2),
    ) -> "ToolIndex":
        index = cls(stubs=list(stubs))
        index.build(hash_dim=hash_dim, ngram_range=ngram_range)
        return index

    def _text_of(self, stub: ToolStub) -> str:
        return stub.searchable_text()

    def build(self, hash_dim: int = 2048, ngram_range: tuple[int, int] = (1, 2)) -> "ToolIndex":
        self._texts = [self._text_of(s) for s in self.stubs]
        self._tfidf = TfidfVectorizer(ngram_range=ngram_range)
        self._dense_vectors = self._tfidf.fit_transform(self._texts)
        self._bm25 = BM25(ngram_range=ngram_range).index(self._texts)
        self._hasher = HashedVectorizer(hash_dim=hash_dim)
        self._hash_vectors = [self._hasher.encode_text(t, ngram_range) for t in self._texts]
        return self

    def dense_scores(self, query: str) -> list[float]:
        """TF-IDF + 余弦相似度。"""
        assert self._tfidf is not None, "先 build()"
        qv = self._tfidf.transform(query)
        return [cosine(qv, dv) for dv in self._dense_vectors]

    def sparse_scores(self, query: str) -> list[float]:
        """BM25 稀疏检索得分。"""
        assert self._bm25 is not None, "先 build()"
        return self._bm25.scores(query)

    def hash_scores(self, query: str) -> list[float]:
        """特征哈希 + 点积（符号哈希内积近似计数）。"""
        assert self._hasher is not None, "先 build()"
        qv = self._hasher.encode_text(query)
        return [dot(qv, hv) for hv in self._hash_vectors]

    def __len__(self) -> int:
        return len(self.stubs)
