# LazyForge

**Agent 工具库按需检索与延迟加载网关** —— 把成百上千个工具从上下文里"卸载"，
任务来了再按语义检索出最相关的 top-k、按需加载 schema。零依赖纯 Python，`doctor` 一键跑通。

> 灵感来源：Google Gemini API 2026-11-19 上线的 **Tool Retrieval** 预览特性
> （`tool_search` + `defer_loading`：智能体让庞大工具库"待命"，只在任务需要时加载工具参数 schema）。

## 👀 3 秒看懂

| 问题 | 答案 |
|---|---|
| 它解决什么 | Agent 工具太多，全量塞上下文太贵；懒加载又怕找错工具 |
| 怎么解决 | stub 常驻 + 语义检索 top-k + defer_loading + 上下文预算 |
| 省多少 | 60 个工具场景，检索模式上下文成本降 **94%** |
| 怎么跑 | `python -m lazyforge doctor`，零依赖零配置 |

## 🚀 30 秒上手

```bash
git clone https://github.com/huzjie/lazyforge.git
cd lazyforge
python -m lazyforge doctor          # 一键冒烟：检索/预算/上下文/执行/评测全链路
python -m lazyforge search "发邮件" -k 3
python -m lazyforge plan   "发邮件"     # 看节省比例
python -m lazyforge benchmark        # 评测报告
```

用你自己的工具库（填一份 JSON/YAML 即可）：

```bash
python -m lazyforge doctor --config examples/config.yaml   # 指向 examples/tools.json
```

## 🧠 核心思路

传统 Agent：把所有工具的 JSON Schema 一次性塞进 system prompt → 上下文成本 O(N)。
LazyForge：只常驻每个工具的 **stub**（名字 + 一句话摘要），任务来了先检索 top-k，再
`defer_loading` 加载这 k 个的完整 schema → 上下文成本降到 O(k)。

```
任务 query → 语义检索(TF-IDF+BM25+特征哈希 混合融合) → 预算决策(load/defer)
          → 组装上下文(stub 全量 + schema 只 top-k) → 分发执行
```

## 📦 干货块

### 干货块 A：中文工具检索的「停用字 + 二元组」分词（可直接抄）

```python
# 中文按字切 + 二元组，但要先去掉量词/虚词，否则「生成一张发票」和
# 「生成一张流程图」会因「一张」撞车误匹配
_CJK_STOP = set("的了是在我你他这那有一二两个些之等把被将给让种份条封篇张门款笔次")

def _cjk_bigrams(text):
    chars = [c for c in re.findall(r"[\u4e00-\u9fff]", text) if c not in _CJK_STOP]
    return chars + ["".join(chars[i:i+2]) for i in range(len(chars)-1)]
```

### 干货块 B：defer_loading 的成本模型（怎么算省了多少）

```
全量成本   = N × (stub_tokens + schema_tokens)
defer 成本 = N × stub_tokens + k × schema_tokens     # 只 top-k 加载 schema
检索成本   = k × (stub_tokens + schema_tokens)       # 只 top-k 进上下文
节省比例(检索) = 1 - k/N                              # 60 工具、k=3 → 95%
```

### 干货块 C：配置片段（`config.yaml`）

```yaml
retrieval:
  top_k: 5
  backend: hybrid          # sparse | dense | hybrid
  hybrid_weight: 0.5
budget:
  context_limit: 12000     # 按你的模型窗口设
  safety_factor: 0.9       # 留 10% 余量
library:
  path: examples/tools.json
```

### 干货块 D：一个可直接复用的「工具库 JSON 条目」

```json
{"name": "send_email", "summary": "发送电子邮件给指定收件人",
 "tags": ["email", "communication"],
 "parameters": {"type": "object",
   "properties": {"to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
   "required": ["to", "subject", "body"]},
 "adapter": "function", "adapter_config": {"name": "send_email"}}
```

## 🏗 项目结构

```
src/lazyforge/
├── registry/    工具模型、注册表、延迟加载器、JSON/YAML 工具库解析
├── embedding/   零依赖分词 + TF-IDF + BM25 + 特征哈希 + 相似度
├── retrieval/   索引、检索器、混合融合、启发式重排
├── budget/      token 成本估计、加载/延迟策略
├── gateway/     一站式编排、上下文组装、分发执行
├── adapters/    function / http / cli / mcp 四类适配器
└── eval/        闭式 oracle + 单调 0-1 指标 + 基准评测
```

零依赖核心 + 可选 PyYAML；Docker / docker-compose / GitHub Actions CI 三件套齐备。

## 🧪 评测

内置 10 条闭式评测任务（真值确定性给出，无需大模型），`doctor` / `benchmark` 输出
`recall@k / MRR / skill / 节省比例`，指标对检索质量单调不减。

## 📄 License

MIT
