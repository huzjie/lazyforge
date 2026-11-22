"""jsonutil —— JSON 序列化辅助：兼容 dataclass / 中文不转义。"""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any


def _to_jsonable(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return obj


def dumps(obj: Any, indent: int = 2) -> str:
    return json.dumps(_to_jsonable(obj), ensure_ascii=False, indent=indent)


def loads(text: str) -> Any:
    return json.loads(text)
