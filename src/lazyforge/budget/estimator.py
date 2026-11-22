"""estimator —— 上下文成本估计：量化「加载哪些工具」要花多少 token。

成本模型（零依赖，用 schema.py 的启发式估算）：
- stub 成本：name + summary 的 token 数（常驻，不随加载变化）
- 完整 schema 成本：JSON Schema 序列化的 token 数（延迟加载的主要开销）
由此可算出「全量加载」vs「按需加载 top-k」的节省幅度，这是 lazyforge 的
核心卖点，也是评测 oracle 的输入。
"""
from __future__ import annotations

from dataclasses import dataclass

from ..registry.schema import estimate_tokens, schema_tokens
from ..registry.tool import Tool, ToolStub


@dataclass
class ToolCost:
    stub_tokens: int
    schema_tokens: int

    @property
    def total(self) -> int:
        return self.stub_tokens + self.schema_tokens


class ContextEstimator:
    def __init__(self, stub_tokens: int = 24, schema_avg_tokens: int = 180) -> None:
        self.stub_tokens = stub_tokens
        self.schema_avg_tokens = schema_avg_tokens

    def stub_cost(self, stub: ToolStub) -> int:
        # 真实估算优先；退化到默认值
        est = estimate_tokens(stub.name + " " + stub.summary)
        return max(est, self.stub_tokens)

    def schema_cost(self, tool: Tool | None) -> int:
        if tool is None:
            return self.schema_avg_tokens
        return max(schema_tokens(tool.parameters), 1)

    def full_library_cost(self, stubs: list[ToolStub], tools: dict[str, Tool]) -> int:
        """全量加载（传统做法）：每个工具 stub + schema 全塞进上下文。"""
        return sum(self.stub_cost(s) for s in stubs) + sum(
            self.schema_cost(tools.get(s.id)) for s in stubs
        )

    def lazy_cost(self, stubs: list[ToolStub], selected: list[ToolStub],
                  tools: dict[str, Tool]) -> int:
        """按需加载（defer_loading）：所有 stub 常驻 + 仅选中工具加载 schema。"""
        stub_total = sum(self.stub_cost(s) for s in stubs)
        schema_total = sum(self.schema_cost(tools.get(s.id)) for s in selected)
        return stub_total + schema_total

    def retrieval_cost(self, selected: list[ToolStub],
                       tools: dict[str, Tool]) -> int:
        """检索模式（tool_search）：只有检索命中的 top-k 工具（stub + schema）进上下文。

        这是 Gemini Tool Retrieval 的核心收益来源：agent 无需在上下文里常驻
        整个工具库，通过 tool_search 按需取，成本随 k 而非 N 增长。
        """
        return sum(
            self.stub_cost(s) + self.schema_cost(tools.get(s.id)) for s in selected
        )
