"""ToolRegistry —— 工具注册表：管理 stub 集合与完整定义，提供增删查与索引。

这是 lazyforge 的「待命工具库」：注册表只常驻 stub，完整 schema 由
DeferredLoader 按需取，是「削减上下文」的第一道闸门。
"""
from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Iterator, Optional

from .loader import DeferredLoader, Loader, MemoryLoader
from .tool import Tool, ToolStub


class ToolRegistry:
    def __init__(self, loader: Optional[Loader] = None) -> None:
        self._stubs: dict[str, ToolStub] = {}
        self._by_tag: dict[str, list[ToolStub]] = defaultdict(list)
        self.loader = DeferredLoader(loader or MemoryLoader())

    # ---- 写入 ------------------------------------------------------------ #
    def register(self, tool: Tool) -> ToolStub:
        """注册完整工具：内存里拆出 stub，完整定义交给 loader。"""
        if isinstance(self.loader._loader, MemoryLoader):  # noqa: SLF001
            self.loader._loader.register(tool)  # noqa: SLF001
        stub = tool.stub
        if not stub.id:
            stub.id = tool.id
        if not stub.adapter:
            stub.adapter = tool.adapter
        self._stubs[stub.id] = stub
        for tag in stub.tags:
            self._by_tag[tag].append(stub)
        return stub

    def add_stub(self, stub: ToolStub) -> None:
        self._stubs[stub.id] = stub
        for tag in stub.tags:
            self._by_tag[tag].append(stub)

    # ---- 读取 ------------------------------------------------------------ #
    def get_stub(self, tool_id: str) -> Optional[ToolStub]:
        return self._stubs.get(tool_id)

    def stubs(self) -> list[ToolStub]:
        return list(self._stubs.values())

    def iter_stubs(self) -> Iterator[ToolStub]:
        yield from self._stubs.values()

    def by_tag(self, tag: str) -> list[ToolStub]:
        return list(self._by_tag.get(tag, []))

    def load(self, stub: ToolStub) -> Optional[Tool]:
        return self.loader.load(stub)

    def load_many(self, stubs: Iterable[ToolStub]) -> dict[str, Tool]:
        return self.loader.load_many(list(stubs))

    def __len__(self) -> int:
        return len(self._stubs)

    def __contains__(self, tool_id: str) -> bool:
        return tool_id in self._stubs
