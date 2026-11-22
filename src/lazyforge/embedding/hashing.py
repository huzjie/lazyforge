"""hashing —— 特征哈希（feature hashing / hashing trick）。

不维护词典、不依赖外部 embedding，直接把任意 token 映射到固定维度稀疏向量，
用于「无词典」场景下的快速 dense-ish 表示。冲突由维度（hash_dim）兜底：
dim 越大冲突越小，这是零依赖检索里性价比最高的「伪 dense」方案。
"""
from __future__ import annotations

from typing import Iterable

from .tokenizer import tokenize


def _fnv1a(s: str, mod: int) -> int:
    h = 0x811C9DC5
    for ch in s.encode("utf-8"):
        h ^= ch
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h % mod


class HashedVectorizer:
    """把 token 序列哈希到 hash_dim 维的稀疏向量（dict: idx -> weight）。"""

    def __init__(self, hash_dim: int = 2048) -> None:
        self.hash_dim = hash_dim

    def encode(self, tokens: Iterable[str]) -> dict[int, float]:
        vec: dict[int, float] = {}
        for tok in tokens:
            idx = _fnv1a(tok, self.hash_dim)
            # 符号哈希：用第二哈希决定 +1/-1，抵消碰撞偏置
            sign = 1.0 if (_fnv1a(tok + "#s", 2) == 0) else -1.0
            vec[idx] = vec.get(idx, 0.0) + sign
        return vec

    def encode_text(self, text: str, ngram_range: tuple[int, int] = (1, 2)) -> dict[int, float]:
        return self.encode(tokenize(text, ngram_range))
