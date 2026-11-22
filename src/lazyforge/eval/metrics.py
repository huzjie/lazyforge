"""metrics —— 检索评测指标：recall@k / MRR / nDCG / 单调 skill。

所有指标都返回 [0,1]，且对「更相关的排序」单调不减 —— 这是「确定性可训练
mock（skill 单调趋 1）」的数学基础：只要检索变好，skill 一定不降。
"""
from __future__ import annotations

import math


def recall_at_k(ranked_ids: list[str], relevant: list[str], k: int) -> float:
    if not relevant:
        return 1.0
    top = set(ranked_ids[:k])
    return len(top & set(relevant)) / len(relevant)


def mrr(ranked_ids: list[str], relevant: list[str]) -> float:
    rel = set(relevant)
    for i, tid in enumerate(ranked_ids):
        if tid in rel:
            return 1.0 / (i + 1)
    return 0.0


def n_dcg(ranked_ids: list[str], relevant: list[str], k: int | None = None) -> float:
    rel = set(relevant)
    k = k or len(ranked_ids)
    top = ranked_ids[:k]
    dcg = sum((1.0 / math.log2(i + 2)) for i, tid in enumerate(top) if tid in rel)
    ideal = sum((1.0 / math.log2(i + 2)) for i in range(min(len(rel), k)))
    return dcg / ideal if ideal else 0.0


def monotone_skill(ranked_ids: list[str], relevant: list[str], k: int = 5) -> float:
    """综合 skill：recall@k 与 MRR 的调和平均，单调非减、取值 [0,1]。"""
    r = recall_at_k(ranked_ids, relevant, k)
    m = mrr(ranked_ids, relevant)
    if r + m == 0:
        return 0.0
    return 2 * r * m / (r + m)
