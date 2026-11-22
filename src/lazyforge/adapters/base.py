"""base —— 工具适配器抽象与统一返回结构。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolResult:
    ok: bool
    output: Any = None
    error: str = ""
    latency_ms: float = 0.0
    meta: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def success(cls, output: Any, latency_ms: float = 0.0, **meta: Any) -> "ToolResult":
        return cls(ok=True, output=output, latency_ms=latency_ms, meta=meta)

    @classmethod
    def failure(cls, error: str, **meta: Any) -> "ToolResult":
        return cls(ok=False, error=error, meta=meta)


class ToolAdapter(ABC):
    """工具适配器：把 Tool 定义 + 参数 -> ToolResult。"""

    name: str = "base"

    @abstractmethod
    def invoke(self, tool: Any, args: dict[str, Any]) -> ToolResult:
        """执行工具；tool 为 registry.Tool，args 为已校验的参数。"""
