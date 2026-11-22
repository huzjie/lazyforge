"""DeferredLoader —— 延迟加载抽象与内存实现。

将「完整工具定义」与「stub 索引」解耦：注册表只持有 stub，完整定义由
Loader 在需要时按 ref 取出。默认 MemoryLoader 一次性把完整定义放进内存，
但对外暴露统一接口，方便替换成「从远程 MCP 服务器 / 数据库 / 文件按需取」。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from .tool import Tool, ToolStub


class Loader(ABC):
    @abstractmethod
    def load(self, stub: ToolStub) -> Optional[Tool]:
        """按 stub 加载完整工具定义；未命中返回 None。"""

    @abstractmethod
    def load_many(self, stubs: list[ToolStub]) -> dict[str, Tool]:
        """批量加载，返回 id -> Tool 映射。"""


class MemoryLoader(Loader):
    """内存加载器：完整定义已驻内存，按 ref/id 索引。"""

    def __init__(self, tools: Optional[list[Tool]] = None) -> None:
        self._index: dict[str, Tool] = {t.id: t for t in (tools or [])}

    def register(self, tool: Tool) -> None:
        self._index[tool.id] = tool

    def load(self, stub: ToolStub) -> Optional[Tool]:
        return self._index.get(stub.id) or self._index.get(stub.ref)

    def load_many(self, stubs: list[ToolStub]) -> dict[str, Tool]:
        out: dict[str, Tool] = {}
        for s in stubs:
            t = self.load(s)
            if t is not None:
                out[s.id] = t
        return out


class DeferredLoader:
    """记录「哪些 stub 已加载」的延迟加载门面，带加载统计。"""

    def __init__(self, loader: Loader) -> None:
        self._loader = loader
        self.loaded_count = 0
        self.deferred_count = 0

    def load(self, stub: ToolStub) -> Optional[Tool]:
        tool = self._loader.load(stub)
        if tool is not None:
            self.loaded_count += 1
        else:
            self.deferred_count += 1
        return tool

    def load_many(self, stubs: list[ToolStub]) -> dict[str, Tool]:
        tools = self._loader.load_many(stubs)
        self.loaded_count += len(tools)
        self.deferred_count += len(stubs) - len(tools)
        return tools

    @property
    def stats(self) -> dict[str, int]:
        return {"loaded": self.loaded_count, "deferred": self.deferred_count}
