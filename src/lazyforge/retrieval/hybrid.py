"""hybrid —— 混合融合：把 dense（TF-IDF）与 sparse（BM25）得分加权合并。

零依赖检索里，TF-IDF 余弦对「同义改写」更鲁棒，BM25 对「精确关键词」更强，
二者互补。融合前先做 min-max 归一化到 [0,1]，否则量纲差会淹没弱信号。
"""
from __future__ import annotations


def _minmax(scores: list[float]) -> list[float]:
    if not scores:
        return []
    lo, hi = min(scores), max(scores)
    if hi - lo < 1e-12:
        return [1.0 if hi > 0 else 0.0 for _ in scores]
    return [(s - lo) / (hi - lo) for s in scores]


class HybridFusion:
    """dense / sparse 得分的加权融合器。"""

    def __init__(self, weight: float = 0.5) -> None:
        self.weight = weight  # dense 权重，1-weight 为 sparse 权重

    def fuse(self, dense: list[float], sparse: list[float]) -> list[float]:
        dn = _minmax(dense)
        sn = _minmax(sparse)
        w = self.weight
        return [w * a + (1 - w) * b for a, b in zip(dn, sn)]

    @staticmethod
    def reciprocal_rank_fusion(rank_lists: list[list[int]], k: float = 60.0) -> dict[int, float]:
        """RRF：按排名倒数融合多个排序列表（无需分数对齐）。

        输入为「按相关度降序的索引列表」，返回 index -> RRF 得分。这是多路
        召回融合的工业标准做法，比分数融合更稳。
        """
        score: dict[int, float] = {}
        for ranks in rank_lists:
            for rank, idx in enumerate(ranks):
                score[idx] = score.get(idx, 0.0) + 1.0 / (k + rank + 1)
        return score
