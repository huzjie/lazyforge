"""mcp —— MCP（Model Context Protocol）工具适配器。

为「把远程 MCP 服务器工具纳入检索」预留的适配器：MCP 工具天然适合
defer_loading —— 服务器上的工具 schema 按需获取，不必全量拉进上下文。
本实现不硬依赖任何 SDK；adapter_config 里给 `endpoint` + `transport`
（stdio / http），执行时通过注册的 transport 函数调用。默认返回占位错误，
保证接口可运行，真实接入替换 transport 即可。
"""
from __future__ import annotations

import time
from typing import Any, Callable

from .base import ToolAdapter, ToolResult

Transport = Callable[[str, str, dict[str, Any]], Any]


class McpAdapter(ToolAdapter):
    name = "mcp"

    def __init__(self, transport: Transport | None = None) -> None:
        self._transport = transport

    def invoke(self, tool: Any, args: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        cfg = tool.adapter_config or {}
        endpoint = cfg.get("endpoint", "")
        tool_name = cfg.get("name") or tool.name
        if self._transport is None:
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.failure(
                "未配置 MCP transport；请设置 adapter_config.transport",
                latency_ms=latency,
            )
        try:
            out = self._transport(endpoint, tool_name, args)
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.success(out, latency_ms=latency)
        except Exception as exc:  # noqa: BLE001
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.failure(str(exc), latency_ms=latency)
