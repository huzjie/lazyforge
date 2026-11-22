"""library —— 从 dict / JSON / YAML 构建工具库。

真实项目里「填写配置即可跑」的关键：把工具库声明为一份 JSON/YAML，每项含
name / summary / description / parameters / tags / adapter 等字段，本模块
解析成 Tool 对象并交给 registry。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .tool import Tool, ToolStub


def build_tool_from_dict(raw: dict[str, Any]) -> Tool:
    name = raw["name"]
    summary = raw.get("summary") or raw.get("description", "")[:80]
    stub = ToolStub(
        id=raw.get("id", name),
        name=name,
        summary=summary,
        tags=list(raw.get("tags", [])),
        ref=raw.get("ref", name),
        adapter=raw.get("adapter", "function"),
        extra=raw.get("extra", {}),
    )
    return Tool(
        id=stub.id,
        name=name,
        description=raw.get("description", summary),
        parameters=raw.get("parameters", {"type": "object", "properties": {}}),
        stub=stub,
        examples=list(raw.get("examples", [])),
        adapter=stub.adapter,
        adapter_config=raw.get("adapter_config", {}),
        cost=raw.get("cost", {}),
    )


def build_tools_from_list(items: list[dict[str, Any]]) -> list[Tool]:
    return [build_tool_from_dict(r) for r in items]


def load_library(path: str | Path) -> list[Tool]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"工具库不存在: {path}")
    if p.suffix in (".yaml", ".yml"):
        try:
            import yaml  # type: ignore
        except ImportError:
            raise RuntimeError("读取 YAML 需安装 pyyaml；或改用 JSON 库文件")
        with p.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    else:
        with p.open("r", encoding="utf-8") as f:
            raw = json.load(f)
    items = raw.get("tools", raw) if isinstance(raw, dict) else raw
    return build_tools_from_list(items)
