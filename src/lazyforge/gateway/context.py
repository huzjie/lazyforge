"""context —— 上下文组装：把检索/预算结果拼成 LLM 可直接消费的工具清单。

输出分两档：
- full：加载 schema 的工具（含完整 JSON Schema）
- stub：延迟加载的工具（只保留名字 + 摘要，agent 需要时再 load）

这是「削减上下文」的最终落点：传统做法是 full 全量，lazyforge 是
「stub 全量 + full 只留 top-k」。
"""
from __future__ import annotations

from typing import Any

from ..budget.policy import Decision, LoadDecision
from ..registry.tool import Tool, ToolStub


class ContextAssembler:
    def assemble(
        self,
        all_stubs: list[ToolStub],
        decisions: list[LoadDecision],
        tools: dict[str, Tool],
    ) -> dict[str, Any]:
        """组装上下文：返回 {tools: [...], stats: {...}}。

        tools 列表元素结构：
          {"name", "summary", "loaded": bool, "schema": {...}|None, "id", "tags"}
        """
        loaded_ids = {d.stub.id for d in decisions if d.decision == Decision.LOAD}
        tool_entries: list[dict[str, Any]] = []
        for stub in all_stubs:
            is_loaded = stub.id in loaded_ids
            tool = tools.get(stub.id)
            entry: dict[str, Any] = {
                "id": stub.id,
                "name": stub.name,
                "summary": stub.summary,
                "tags": stub.tags,
                "loaded": is_loaded,
                "schema": tool.parameters if (is_loaded and tool) else None,
            }
            tool_entries.append(entry)

        n_load = len(loaded_ids)
        n_defer = len(all_stubs) - n_load
        return {
            "tools": tool_entries,
            "stats": {
                "total": len(all_stubs),
                "loaded": n_load,
                "deferred": n_defer,
            },
        }
