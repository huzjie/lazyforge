"""registry —— 适配器工厂：按名称取适配器实例。"""
from __future__ import annotations

from .base import ToolAdapter
from .cli import CliAdapter
from .function import FunctionAdapter
from .http import HttpAdapter
from .mcp import McpAdapter

_BUILTIN: dict[str, type[ToolAdapter]] = {
    "function": FunctionAdapter,
    "http": HttpAdapter,
    "cli": CliAdapter,
    "mcp": McpAdapter,
}


def get_adapter(name: str, **kwargs) -> ToolAdapter:
    cls = _BUILTIN.get(name)
    if cls is None:
        raise ValueError(f"未知适配器: {name}（可用: {sorted(_BUILTIN)}）")
    return cls(**kwargs)
