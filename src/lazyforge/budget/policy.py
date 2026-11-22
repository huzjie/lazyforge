"""policy —— 预算策略：在预算约束下决定「加载哪些工具、延迟哪些」。

三种决策：
- LOAD：加载完整 schema（top-k 命中）
- DEFER：只保留 stub，等 agent 显式需要时再加载（defer_loading）
- OVER：预算已满，连 stub 都精简到只留名字

策略核心：只要「所有 stub + top-k schema」在 context_limit 内，就全量 load
top-k；超限则按分数降级，把低分工具的 schema 标记为 defer。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ..registry.tool import Tool, ToolStub
from .estimator import ContextEstimator


class Decision(Enum):
    LOAD = "load"
    DEFER = "defer"
    OVER = "over"


@dataclass
class LoadDecision:
    stub: ToolStub
    decision: Decision
    cost: int = 0


@dataclass
class BudgetPolicy:
    context_limit: int = 12000
    safety_factor: float = 0.9
    estimator: ContextEstimator = field(default_factory=ContextEstimator)

    def _effective_limit(self) -> int:
        return int(self.context_limit * self.safety_factor)

    def decide(
        self,
        ranked_stubs: list[ToolStub],
        all_stubs: list[ToolStub],
        tools: dict[str, Tool],
    ) -> list[LoadDecision]:
        """对按相关度降序排列的候选 stub 做加载决策。"""
        limit = self._effective_limit()
        # 所有 stub 常驻（这是延迟加载的前提：agent 至少知道有哪些工具）
        used = sum(self.estimator.stub_cost(s) for s in all_stubs)
        decisions: list[LoadDecision] = []
        for stub in ranked_stubs:
            cost = self.estimator.schema_cost(tools.get(stub.id))
            if used + cost <= limit:
                decisions.append(LoadDecision(stub, Decision.LOAD, cost))
                used += cost
            else:
                decisions.append(LoadDecision(stub, Decision.DEFER, 0))
        return decisions

    def is_within_budget(self, all_stubs: list[ToolStub], selected: list[ToolStub],
                         tools: dict[str, Tool]) -> bool:
        return self.estimator.lazy_cost(all_stubs, selected, tools) <= self._effective_limit()
