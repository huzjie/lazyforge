"""lazyforge — Agent 工具库按需检索与延迟加载网关。

核心思想：智能体面对成百上千个工具时，不必把所有工具的完整 JSON Schema
一次性塞进上下文。lazyforge 只常驻每个工具的「stub」（名字 + 一句话摘要），
用零依赖的 TF-IDF + 特征哈希做语义检索，任务来了只检索出最相关的 top-k 个
工具，再按需（defer_loading）加载其完整 schema —— 把上下文成本从 O(N) 压到
O(k)。

模块：
- registry   工具注册表与延迟加载器
- embedding  零依赖稀疏向量化（TF-IDF + 特征哈希 + BM25）
- retrieval  语义检索 + 混合融合 + 重排
- budget     上下文预算估计与加载/延迟策略
- gateway    检索 -> 延迟加载 -> 分发执行 的一站式入口
- adapters   function / http / cli / mcp 四类工具适配器
- eval       闭式 oracle + 可验证 reward + 单调 0-1 指标
"""

from .version import __version__

__all__ = ["__version__"]
