"""benchmark —— 基准评测：对整个数据集跑检索 + oracle 判定，汇总报告。"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..gateway.gateway import LazyGateway
from .dataset import Task, build_default_dataset
from .oracle import Oracle


@dataclass
class BenchmarkReport:
    per_task: list[dict] = field(default_factory=list)
    avg_recall: float = 0.0
    avg_mrr: float = 0.0
    avg_skill: float = 0.0
    avg_savings: float = 0.0
    avg_retrieval_savings: float = 0.0
    hit_rate: float = 0.0

    def to_dict(self) -> dict:
        return {
            "avg_recall@k": round(self.avg_recall, 4),
            "avg_mrr": round(self.avg_mrr, 4),
            "avg_skill": round(self.avg_skill, 4),
            "avg_savings_ratio": round(self.avg_savings, 4),
            "avg_retrieval_savings": round(self.avg_retrieval_savings, 4),
            "hit_rate": round(self.hit_rate, 4),
            "n_tasks": len(self.per_task),
            "per_task": self.per_task,
        }


def benchmark(
    gateway: LazyGateway,
    tasks: list[Task] | None = None,
    k: int = 5,
) -> BenchmarkReport:
    tasks = tasks or build_default_dataset()
    oracle = Oracle(k=k)
    report = BenchmarkReport()
    for task in tasks:
        ranked_ids = gateway.searcher.search_ids(task.query, top_k=k)
        verdict = oracle.judge(task, ranked_ids)
        plan = gateway.plan(task.query, top_k=k)
        report.per_task.append({
            "query": task.query,
            "relevant": task.relevant_ids,
            "retrieved": ranked_ids,
            **verdict.to_dict(),
            "savings_ratio": round(plan.savings_ratio, 4),
            "retrieval_savings_ratio": round(plan.retrieval_savings_ratio, 4),
        })
    n = len(report.per_task) or 1
    report.avg_recall = sum(t["recall@k"] for t in report.per_task) / n
    report.avg_mrr = sum(t["mrr"] for t in report.per_task) / n
    report.avg_skill = sum(t["skill"] for t in report.per_task) / n
    report.avg_savings = sum(t["savings_ratio"] for t in report.per_task) / n
    report.avg_retrieval_savings = sum(
        t["retrieval_savings_ratio"] for t in report.per_task) / n
    report.hit_rate = sum(1 for t in report.per_task if t["hit"]) / n
    return report
