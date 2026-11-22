# 调参指南

## 检索相关（config.yaml → retrieval）

| 参数 | 默认 | 说明 | 建议 |
|---|---|---|---|
| `top_k` | 5 | 每个任务检索出的候选数 | 工具少用 3，工具多（>200）用 8~10 |
| `backend` | hybrid | sparse / dense / hybrid | 精确关键词多用 sparse；同义改写多用 hybrid |
| `hybrid_weight` | 0.5 | dense 融合权重 | 中文短查询可提到 0.6~0.7 |

## 嵌入相关（embedding）

| 参数 | 默认 | 说明 |
|---|---|---|
| `hash_dim` | 2048 | 特征哈希维度，越大碰撞越少 |
| `ngram_range` | [1, 2] | 中文二元组覆盖「发送邮件」这类词组 |
| `idf_smoothing` | 0.5 | 平滑因子，语料小可调大 |

## 预算相关（budget）

| 参数 | 默认 | 说明 |
|---|---|---|
| `context_limit` | 12000 | 目标上下文 token 上限，按你的模型窗口设 |
| `schema_avg_tokens` | 180 | 无完整 schema 时的估算兜底 |
| `safety_factor` | 0.9 | 留 10% 余量 |

## 三个避坑点

1. **stub 摘要要写「动作 + 对象」**：`发送邮件` 而不是 `邮件`，检索全靠这一句。
2. **工具名带动作动词**：`send_email` / `read_file` 比 `email` / `file` 好，
   重排器对「名字命中」有强 boost。
3. **预算别卡太死**：`safety_factor` 太低会频繁 defer 导致 agent 反复加载，
   反而更贵；先给 0.9，再按实测收紧。
