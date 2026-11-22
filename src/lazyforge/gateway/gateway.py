"""gateway —— LazyGateway：lazyforge 的一站式入口。

把 registry / index / searcher / policy / estimator / context / dispatcher
串成一条「任务 -> 检索 -> 预算 -> 加载 -> 上下文/执行」的完整链路。

典型用法：
    gw = LazyGateway.from_tools(tools, config)
    plan = gw.plan("给客户发一封项目周报邮件")   # 检索 + 预算决策 + 组装上下文
    result = gw.run("发送邮件", {"to": "...", "subject": "...", "body": "..."})
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..adapters import ToolResult
from ..budget.estimator import ContextEstimator
from ..budget.policy import BudgetPolicy, Decision, LoadDecision
from ..config import Config
from ..registry.loader import MemoryLoader
from ..registry.registry import ToolRegistry
from ..registry.tool import Tool, ToolStub
from ..retrieval.index import ToolIndex
from ..retrieval.searcher import Searcher
from .context import ContextAssembler
from .dispatcher import Dispatcher


@dataclass
class GatewayPlan:
    task: str
    ranked: list
    decisions: list[LoadDecision] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    full_cost: int = 0
    lazy_cost: int = 0
    retrieval_cost: int = 0

    @property
    def savings_ratio(self) -> float:
        if self.full_cost <= 0:
            return 0.0
        return 1.0 - self.lazy_cost / self.full_cost

    @property
    def retrieval_savings_ratio(self) -> float:
        """检索模式（只取 top-k 进上下文）相对全量库的节省比例。"""
        if self.full_cost <= 0:
            return 0.0
        return 1.0 - self.retrieval_cost / self.full_cost

    @property
    def loaded_tools(self) -> list[ToolStub]:
        return [d.stub for d in self.decisions if d.decision == Decision.LOAD]


class LazyGateway:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self.registry = ToolRegistry(MemoryLoader())
        self.estimator = ContextEstimator(
            stub_tokens=self.config.budget.stub_tokens,
            schema_avg_tokens=self.config.budget.schema_avg_tokens,
        )
        self.policy = BudgetPolicy(
            context_limit=self.config.budget.context_limit,
            safety_factor=self.config.budget.safety_factor,
            estimator=self.estimator,
        )
        self.index: ToolIndex | None = None
        self.searcher: Searcher | None = None
        self.assembler = ContextAssembler()
        self.dispatcher = Dispatcher()

    # ---- 构建 ------------------------------------------------------------ #
    def register(self, tool: Tool) -> None:
        self.registry.register(tool)

    def register_many(self, tools: list[Tool]) -> None:
        for t in tools:
            self.register(t)

    def build_index(self) -> None:
        self.index = ToolIndex.from_stubs(
            self.registry.stubs(),
            hash_dim=self.config.embedding.hash_dim,
            ngram_range=self.config.embedding.ngram_range,
        )
        self.searcher = Searcher(
            self.index,
            backend=self.config.retrieval.backend,
            hybrid_weight=self.config.retrieval.hybrid_weight,
        )

    @classmethod
    def from_tools(cls, tools: list[Tool], config: Config | None = None) -> "LazyGateway":
        gw = cls(config)
        gw.register_many(tools)
        gw.build_index()
        return gw

    # ---- 规划（检索 + 预算 + 上下文） ------------------------------------ #
    def plan(self, task: str, top_k: int | None = None) -> GatewayPlan:
        assert self.searcher is not None, "先 build_index()"
        k = top_k or self.config.retrieval.top_k
        ranked = self.searcher.search(task, top_k=k)
        all_stubs = self.registry.stubs()
        tools = self.registry.load_many([r.stub for r in ranked])

        decisions = self.policy.decide([r.stub for r in ranked], all_stubs, tools)
        context = self.assembler.assemble(all_stubs, decisions, tools)

        full_cost = self.estimator.full_library_cost(
            all_stubs, self.registry.load_many(all_stubs))
        lazy_cost = self.estimator.lazy_cost(
            all_stubs, [d.stub for d in decisions], tools)
        selected_stubs = [d.stub for d in decisions if d.decision == Decision.LOAD]
        retrieval_cost = self.estimator.retrieval_cost(selected_stubs, tools)

        return GatewayPlan(
            task=task, ranked=ranked, decisions=decisions, context=context,
            full_cost=full_cost, lazy_cost=lazy_cost,
            retrieval_cost=retrieval_cost,
        )

    # ---- 执行 ------------------------------------------------------------ #
    def run(self, task: str, args: dict[str, Any], top_k: int = 1) -> ToolResult:
        """按任务检索最相关工具并执行。返回 ToolResult。"""
        plan = self.plan(task, top_k=top_k)
        if not plan.ranked:
            return ToolResult.failure("没有检索到匹配工具")
        stub = plan.ranked[0].stub
        tool = self.registry.load(stub)
        if tool is None:
            return ToolResult.failure(f"工具 {stub.name} 定义缺失")
        return self.dispatcher.invoke(tool, args)
