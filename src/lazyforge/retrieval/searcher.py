"""searcher —— 检索器：把 query 映射为排序后的 (stub, score) 列表。

支持 sparse / dense / hybrid 三种后端，内部走 index 打分 -> rerank 重排 ->
top-k 截断。这是「任务来了该加载哪些工具」的核心决策点。
"""
from __future__ import annotations

from dataclasses import dataclass

from ..registry.tool import ToolStub
from .hybrid import HybridFusion
from .index import ToolIndex
from .rerank import Reranker


@dataclass
class ScoredTool:
    stub: ToolStub
    score: float
    rank: int


class Searcher:
    def __init__(
        self,
        index: ToolIndex,
        backend: str = "hybrid",
        hybrid_weight: float = 0.5,
        reranker: Reranker | None = None,
    ) -> None:
        self.index = index
        self.backend = backend
        self.hybrid = HybridFusion(weight=hybrid_weight)
        self.reranker = reranker or Reranker()

    def _raw_scores(self, query: str) -> list[float]:
        if self.backend == "sparse":
            return self.index.sparse_scores(query)
        if self.backend == "dense":
            return self.index.dense_scores(query)
        # hybrid：dense + sparse 加权融合
        dense = self.index.dense_scores(query)
        sparse = self.index.sparse_scores(query)
        return self.hybrid.fuse(dense, sparse)

    def search(self, query: str, top_k: int = 5) -> list[ScoredTool]:
        if not self.index.stubs:
            return []
        raw = self._raw_scores(query)
        reranked = self.reranker.rerank(query, self.index.stubs, raw)
        ranked = sorted(
            enumerate(reranked), key=lambda x: x[1], reverse=True
        )[:top_k]
        return [
            ScoredTool(stub=self.index.stubs[i], score=s, rank=r)
            for r, (i, s) in enumerate(ranked)
        ]

    def search_ids(self, query: str, top_k: int = 5) -> list[str]:
        return [s.stub.id for s in self.search(query, top_k)]
