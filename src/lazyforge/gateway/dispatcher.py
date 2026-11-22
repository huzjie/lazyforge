"""dispatcher —— 工具分发：参数校验 + 适配器调用 + 统一异常兜底。"""
from __future__ import annotations

from typing import Any

from ..adapters import ToolResult, get_adapter
from ..registry.schema import validate_parameters
from ..registry.tool import Tool


class Dispatcher:
    def __init__(self, adapters: dict[str, Any] | None = None) -> None:
        self._adapters = adapters or {}
        self._cache: dict[str, Any] = {}

    def _adapter(self, tool: Tool):
        name = tool.adapter or "function"
        if name not in self._cache:
            self._cache[name] = self._adapters.get(name) or get_adapter(name)
        return self._cache[name]

    def validate(self, tool: Tool, args: dict[str, Any]) -> list[str]:
        return validate_parameters(tool.parameters, args)

    def invoke(self, tool: Tool, args: dict[str, Any]) -> ToolResult:
        errors = self.validate(tool, args)
        if errors:
            return ToolResult.failure("; ".join(errors))
        return self._adapter(tool).invoke(tool, args)
