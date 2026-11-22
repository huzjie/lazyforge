"""schema —— 工具 JSON Schema 的校验、序列化与体积估算。

体积估算是预算引擎的关键输入：一个工具的「上下文成本」≈ 其 JSON Schema
序列化后的 token 数，这里用零依赖启发式（近似 OpenAI tokenizer 的 4 字节/token
规则 + 结构性修正）在「不真跑 tokenizer」的前提下给出可靠下界。
"""
from __future__ import annotations

import json
from typing import Any


def schema_to_json(schema: dict[str, Any]) -> str:
    """把 JSON Schema 字典序列化为紧凑字符串（无空格，用于体积估计）。"""
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


def estimate_tokens(text: str) -> int:
    """零依赖 token 估算：中文按字、其余按 ~4 字节/token 的混合规则。

    更贴近真实 tokenizer 的下界：数字/ASCII 连续串按 4 字节切，CJK 逐字计。
    """
    if not text:
        return 0
    tokens = 0
    buf = ""
    for ch in text:
        if ord(ch) > 0x2E80:  # CJK 及全角，逐字算 1 token
            if buf:
                tokens += max(1, (len(buf.encode("utf-8")) + 3) // 4)
                buf = ""
            tokens += 1
        elif ch in " \t\n":
            if buf:
                tokens += max(1, (len(buf.encode("utf-8")) + 3) // 4)
                buf = ""
        else:
            buf += ch
    if buf:
        tokens += max(1, (len(buf.encode("utf-8")) + 3) // 4)
    return tokens


def schema_tokens(schema: dict[str, Any]) -> int:
    """估算一个工具 JSON Schema 占用的 token 数。"""
    return estimate_tokens(schema_to_json(schema))


def validate_parameters(schema: dict[str, Any], args: dict[str, Any]) -> list[str]:
    """轻量参数校验：返回缺失/类型不匹配的错误列表（空列表 = 通过）。

    只做工程上必要的强约束（required + type），不做完整 JSON Schema 验证，
    避免重依赖，同时挡住最常踩的坑。
    """
    errors: list[str] = []
    props: dict[str, Any] = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in args:
            errors.append(f"缺少必填参数: {name}")
    type_map = {"string": str, "integer": int, "number": (int, float),
                "boolean": bool, "array": list, "object": dict}
    for name, value in args.items():
        spec = props.get(name, {})
        expected = spec.get("type")
        if expected is None:
            continue
        want = type_map.get(expected)
        if want is None:
            continue
        if value is None:
            continue
        if not isinstance(value, want):
            errors.append(f"参数 {name} 类型错误: 期望 {expected}")
    return errors
