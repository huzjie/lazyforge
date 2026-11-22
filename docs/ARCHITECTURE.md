# 架构设计

## 一句话

Agent 面对成百上千个工具时，不必把所有工具 JSON Schema 塞进上下文；lazyforge
只常驻轻量 stub，任务来了按语义检索 top-k，再 `defer_loading` 加载完整 schema。

## 数据流

```
用户任务 query
      │
      ▼
┌─────────────┐   search()   ┌──────────────┐   decide()   ┌──────────────┐
│ ToolIndex    │ ───────────▶ │   Searcher    │ ───────────▶ │ BudgetPolicy  │
│ (stub 常驻)  │  稀疏/稠密/混合 │  (排序 top-k) │  加载/延迟     │  (预算决策)    │
└─────────────┘              └──────────────┘              └──────┬───────┘
                                                                  ▼
                                                            ┌──────────────┐
                                                            │ ContextAssembler│
                                                            │ stub全量+full只top-k│
                                                            └──────┬───────┘
                                                                   ▼
                                                          Dispatcher.invoke()
                                                          （参数校验 + 适配器执行）
```

## 模块职责

| 模块 | 文件 | 职责 |
|---|---|---|
| registry | tool.py / registry.py / loader.py | 工具数据模型、stub 注册表、延迟加载器 |
| embedding | tokenizer / tfidf / bm25 / hashing / vectors | 零依赖向量化与相似度 |
| retrieval | index / searcher / hybrid / rerank | 索引、检索、混合融合、重排 |
| budget | estimator / policy | token 成本估计、加载/延迟决策 |
| gateway | gateway / context / dispatcher | 一站式编排、上下文组装、分发执行 |
| adapters | function / http / cli / mcp | 四类工具执行适配器 |
| eval | dataset / metrics / oracle / benchmark | 闭式真值评测、单调指标 |

## 三个核心设计决策

1. **stub 与 schema 解耦**：注册表只持有 stub（名字 + 一句话摘要 + tags），
   完整 schema 由 `DeferredLoader` 按需取。上下文成本从 `O(N × schema)` 降到
   `O(N × stub + k × schema)`。

2. **零依赖稀疏检索**：TF-IDF + 特征哈希 + BM25，无需外部 embedding API 或
   稠密矩阵，数百工具规模下够快够省；中文按字 + 二元组切分，英文按词。

3. **可验证评测**：真值是闭式确定的（每个任务明确列出应命中工具 id），
   recall@k / MRR / skill 单调不减，检索变好 skill 一定不降，无需大模型参与。
