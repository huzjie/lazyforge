"""function —— 本地函数适配器：通过注册表把工具名映射到 Python 可调用对象。

这是最常见的工具类型：agent 工具本质是一个 Python 函数。adapter_config 里
给 `callable` 即可；为避免硬编码依赖，允许传 `name` 走一个全局函数注册表。
"""
from __future__ import annotations

import time
from typing import Any, Callable

from .base import ToolAdapter, ToolResult

_FUNCTION_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_function(name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """装饰器：把函数注册到全局函数表，供 FunctionAdapter 按名调用。"""

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        _FUNCTION_REGISTRY[name] = fn
        return fn

    return decorator


class FunctionAdapter(ToolAdapter):
    name = "function"

    def __init__(self, registry: dict[str, Callable[..., Any]] | None = None) -> None:
        self._registry = registry or {}

    def register(self, name: str, fn: Callable[..., Any]) -> None:
        self._registry[name] = fn

    def _resolve(self, tool: Any) -> Callable[..., Any]:
        cfg = tool.adapter_config or {}
        fn = cfg.get("callable")
        if callable(fn):
            return fn
        name = cfg.get("name") or tool.name
        fn = self._registry.get(name) or _FUNCTION_REGISTRY.get(name)
        if fn is None:
            raise KeyError(f"函数未注册: {name}")
        return fn

    def invoke(self, tool: Any, args: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        try:
            fn = self._resolve(tool)
            out = fn(**args) if isinstance(args, dict) else fn(args)
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.success(out, latency_ms=latency)
        except Exception as exc:  # noqa: BLE001
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.failure(str(exc), latency_ms=latency)
