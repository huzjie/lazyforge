"""rerank —— 启发式重排：在语义打分之上叠加可解释的强信号。

检索召回 top-N 后，用几个「便宜又有效」的信号二次排序：
- 工具名 / 标签 与 query 的精确词命中（强 boost）
- 摘要关键词覆盖率（软 boost）
这些信号对「工具名高度相关的任务」极其关键——用户说"发邮件"时，
`send_email` 这个名字本身就该压过泛泛的 `notify`。
"""
from __future__ import annotations

import re
from typing import Iterable

from ..registry.tool import ToolStub


def _terms(query: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]", query.lower()))


class Reranker:
    def __init__(self, name_boost: float = 1.5, tag_boost: float = 0.8) -> None:
        self.name_boost = name_boost
        self.tag_boost = tag_boost

    def rerank(
        self,
        query: str,
        stubs: list[ToolStub],
        base_scores: list[float],
    ) -> list[float]:
        """在 base_scores 基础上叠加名称/标签命中 boost，返回新得分。"""
        q = _terms(query)
        if not q:
            return list(base_scores)
        out: list[float] = []
        for stub, base in zip(stubs, base_scores):
            boost = 0.0
            name_terms = _terms(stub.name)
            if q & name_terms:
                boost += self.name_boost
            tag_terms = set()
            for t in stub.tags:
                tag_terms |= _terms(t)
            if q & tag_terms:
                boost += self.tag_boost
            out.append(base * (1.0 + boost))
        return out
