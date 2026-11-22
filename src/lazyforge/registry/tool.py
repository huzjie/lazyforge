"""工具数据模型：stub（常驻，轻量）与 Tool（完整，延迟加载）。

设计要点：Agent 上下文里常驻的是 ToolStub（name + 一句话摘要 + tags + 引用），
只有检索命中后才通过 DeferredLoader 把完整 Tool（含 JSON Schema 参数定义、
示例、成本元数据）加载进上下文 —— 这正是 Gemini Tool Retrieval 里
`defer_loading` 的工程化落地。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ParameterSpec:
    """单个参数的轻量描述（用于 schema 体积估算，无需完整 JSON Schema）。"""
    name: str
    type: str = "string"
    required: bool = False


@dataclass
class ToolStub:
    """常驻索引里的轻量条目。上下文成本只与 stub 数量线性相关。"""
    id: str
    name: str
    summary: str                       # 一句话描述（检索与展示都靠它）
    tags: list[str] = field(default_factory=list)
    ref: str = ""                      # 完整定义的引用键（文件名/URI/注册键）
    adapter: str = "function"          # function | http | cli | mcp
    extra: dict[str, Any] = field(default_factory=dict)

    def searchable_text(self) -> str:
        return " ".join([self.name, self.summary, *self.tags])


@dataclass
class Tool:
    """完整工具定义，仅在命中 top-k 后按需加载。"""
    id: str
    name: str
    description: str
    parameters: dict[str, Any]         # 完整 JSON Schema（properties/required/...）
    stub: ToolStub
    examples: list[dict[str, Any]] = field(default_factory=list)
    adapter: str = "function"
    adapter_config: dict[str, Any] = field(default_factory=dict)
    cost: dict[str, Any] = field(default_factory=dict)

    def param_names(self) -> list[str]:
        props = self.parameters.get("properties", {})
        return list(props.keys())

    def required_names(self) -> list[str]:
        return list(self.parameters.get("required", []))

    @classmethod
    def from_stub(cls, stub: ToolStub, description: str, parameters: dict[str, Any]) -> "Tool":
        return cls(
            id=stub.id, name=stub.name, description=description,
            parameters=parameters, stub=stub, adapter=stub.adapter,
        )
