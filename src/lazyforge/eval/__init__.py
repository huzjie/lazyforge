"""eval —— 闭式 oracle + 可验证 reward + 单调 0-1 指标。"""
from .dataset import Task, build_default_dataset
from .metrics import recall_at_k, mrr, n_dcg, monotone_skill
from .oracle import Oracle
from .benchmark import benchmark

__all__ = ["Task", "build_default_dataset", "recall_at_k", "mrr", "n_dcg",
           "monotone_skill", "Oracle", "benchmark"]
