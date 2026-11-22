"""配置加载：统一从 YAML / JSON / 默认值解析 lazyforge 运行参数。

零依赖设计：优先尝试 PyYAML，缺失时退化为 JSON / 内建默认值，
保证 `python -m lazyforge doctor` 在裸 Python 环境也能跑通。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return _load_json(path)
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class RetrievalConfig:
    top_k: int = 5
    backend: str = "hybrid"          # sparse | dense | hybrid
    hybrid_weight: float = 0.5       # dense 权重

    def __post_init__(self) -> None:
        if self.backend not in ("sparse", "dense", "hybrid"):
            raise ValueError(f"未知检索后端: {self.backend}")


@dataclass
class EmbeddingConfig:
    hash_dim: int = 2048
    ngram_range: tuple[int, int] = (1, 2)
    idf_smoothing: float = 0.5
    min_df: int = 1
    max_features: int = 1 << 16


@dataclass
class BudgetConfig:
    context_limit: int = 12000
    schema_avg_tokens: int = 180
    stub_tokens: int = 24
    safety_factor: float = 0.9


@dataclass
class LibraryConfig:
    format: str = "json"             # json | yaml
    path: str = ""                   # 留空则用内置 60 工具演示库


@dataclass
class Config:
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    budget: BudgetConfig = field(default_factory=BudgetConfig)
    library: LibraryConfig = field(default_factory=LibraryConfig)

    @classmethod
    def load(cls, path: str | Path | None = None) -> "Config":
        cfg = cls()
        if not path:
            return cfg
        p = Path(path)
        if not p.exists():
            return cfg
        raw = _load_yaml(p) if p.suffix in (".yaml", ".yml") else _load_json(p)
        cfg._apply(raw)
        return cfg

    def _apply(self, raw: dict[str, Any]) -> None:
        if not raw:
            return
        for section in ("retrieval", "embedding", "budget", "library"):
            if section in raw and isinstance(raw[section], dict):
                target = getattr(self, section)
                for k, v in raw[section].items():
                    if hasattr(target, k):
                        setattr(target, k, v)
