"""oracle —— 闭式 oracle：确定性判定检索结果与真值的一致性。

不调用大模型、不依赖随机性：给定 Searcher 返回的工具 id 序列与 Task 的
relevant_ids，直接算出 recall / MRR / skill。这是「可复现评测」的根基。
"""
from __future__ import annotations

from dataclasses import dataclass

from .dataset import Task
from .metrics import mrr, monotone_skill, recall_at_k


@dataclass
class OracleVerdict:
    recall_at_k: float
    mrr: float
    skill: float
    hit: bool

    def to_dict(self) -> dict[str, float | bool]:
        return {
            "recall@k": round(self.recall_at_k, 4),
            "mrr": round(self.mrr, 4),
            "skill": round(self.skill, 4),
            "hit": self.hit,
        }


class Oracle:
    def __init__(self, k: int = 5) -> None:
        self.k = k

    def judge(self, task: Task, ranked_ids: list[str]) -> OracleVerdict:
        r = recall_at_k(ranked_ids, task.relevant_ids, self.k)
        m = mrr(ranked_ids, task.relevant_ids)
        s = monotone_skill(ranked_ids, task.relevant_ids, self.k)
        return OracleVerdict(recall_at_k=r, mrr=m, skill=s,
                             hit=task.relevant_ids[0] in ranked_ids[:self.k])
