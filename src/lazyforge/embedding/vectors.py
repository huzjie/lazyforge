"""vectors —— 稀疏向量的相似度计算（点积 / 余弦 / L2）。

所有检索后端最终都落到这里：给定 query 向量与若干 doc 向量，返回相似度。
向量用 dict 表示（key 为词项或哈希索引），点积只遍历较短的一侧。
"""
from __future__ import annotations

import math
from typing import Iterable


def dot(a: dict, b: dict) -> float:
    if len(a) > len(b):
        a, b = b, a
    return sum(w * b.get(k, 0.0) for k, w in a.items())


def _norm(v: dict) -> float:
    s = sum(w * w for w in v.values())
    return math.sqrt(s) if s else 0.0


def cosine(a: dict, b: dict) -> float:
    na, nb = _norm(a), _norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot(a, b) / (na * nb)


def l2(a: dict, b: dict) -> float:
    keys = set(a) | set(b)
    s = sum((a.get(k, 0.0) - b.get(k, 0.0)) ** 2 for k in keys)
    return math.sqrt(s)


def topk(scores: Iterable[float], k: int) -> list[int]:
    """返回得分最高的 k 个索引（稳定，按分数降序）。"""
    indexed = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    return [i for i, _ in indexed[:k]]
