# 技术篇｜Agent 工具库「按需检索 + 延迟加载」怎么落地：从 Gemini Tool Retrieval 到零依赖实现

> 一句话：与其把几百个工具的 JSON Schema 全塞进上下文，不如只留「名字 + 一句话摘要」常驻，
> 任务来了先用语义检索捞出最相关的 top-k，再按需加载这 k 个的完整定义。上下文成本从 O(N) 压到 O(k)。

## 一、背景：这次不是"又发了个模型"，而是 Agent 上下文的一次成本革命

2026-11-19，Google 在 Gemini Interactions API 上线了 **Tool Retrieval** 预览——给智能体两个新能力：
`tool_search`（让 Agent 把庞大工具库"待命"，只在任务需要时搜索相关工具）和 `defer_loading`
（工具的参数 schema 按需加载，不必一次性全进上下文）。同日发布的还有 Gemini 4 Neon、Genie 4 等，
但真正值得工程界照抄的是这个：**它直击 Agent 规模化后最疼的一个瓶颈——上下文窗口被工具定义撑爆**。

一个真实数字：一个 enterprise Agent 挂 200 个工具、每个工具 JSON Schema 平均 180 token，光工具定义就要
吃掉 3.6 万 token——还没开始干活，窗口先烧掉一大截。Tool Retrieval 的思路是把这 3.6 万压到「只留
top-k 的几百 token」。

我把这套机制用**零依赖纯 Python**完整实现了一遍（LazyForge），下面拆给你看原理和可复用的工程技巧。

## 二、技术原理拆解：五个子系统

### ① stub 与 schema 解耦（defer_loading 的根基）

Agent 上下文里常驻的不是完整工具，而是**轻量 stub**——名字 + 一句话摘要 + 标签 + 引用。完整定义
（JSON Schema 参数、示例、成本元数据）由 `DeferredLoader` 按 ref 取。这一步是"削减上下文"的第一道闸门：
内存里只保留 `O(N × stub)` 的轻量索引，`O(N × schema)` 的沉重点餐制加载。

### ② 零依赖语义检索：TF-IDF + 特征哈希 + BM25

不调外部 embedding API、不建稠密矩阵。三个表示并存：TF-IDF（dense-ish 稀疏向量）、BM25（经典稀疏检索）、
特征哈希（无词典快速匹配）。中文按字切 + 二元组，英文按词切，落在同一稀疏空间里，点积/余弦就能算相似度。

### ③ 混合融合 + 启发式重排

TF-IDF 对同义改写更鲁棒，BM25 对精确关键词更强，二者 min-max 归一化后加权融合；再用**重排器**叠加两个
便宜又有效的强信号——工具名命中 query 词（强 boost）、标签命中（软 boost）。"发邮件"就该把 `send_email`
压在泛泛的 `notify` 之上。

### ④ 上下文预算引擎

零依赖估算 token（中文按字、ASCII 按 4 字节/token），算清「全量加载 vs defer vs 检索」三种成本，在
`context_limit` 约束下决定每个工具 `load / defer`。预算超了就按分数降级，把低分工具 schema 标记 defer。

### ⑤ 四类适配器统一分发

function（本地函数）、http（REST 调用）、cli（子进程）、mcp（远程 MCP 服务器）——统一 `invoke(tool, args)`
接口 + 参数校验 + 异常兜底。MCP 工具天然适合 defer_loading，因为它本就在远程、按需取。

## 三、可复用思路（工程技巧，可直接照抄）

1. **stub 摘要写「动作 + 对象」**：`发送邮件` 而非 `邮件`。检索全靠这一句，写糊了整个库就废了。
2. **中文分词先加停用字表**：去掉「一张/两个/一段/的」这类量词和虚词，否则"生成一张发票"和
   "生成一张流程图"会因"一张"撞车误匹配——这是零依赖中文检索最容易踩、也最隐蔽的坑。
3. **成本模型三档分开算**：defer 只省 schema、不省 stub；检索连 stub 都省。想吹"省 90%"就说检索模式，
   想保守就说 defer 模式，口径别混。
4. **评测用「闭式 oracle」**：真值确定性给出（每个任务列出应命中的工具 id），recall@k / MRR / skill 单调
   不减，检索变好指标一定不降——不用大模型打分也能复现。
5. **符号哈希抵消碰撞偏置**：特征哈希时用第二哈希决定 +1/-1，抵消维度冲突的系统性偏差。

## 四、干货块：提示词 / 工作流模板

### 模板 1：让 LLM 先"搜工具"再"选工具"的 system prompt 片段

```
你是一个工具调用智能体。可用工具通过 tool_search(query) 按需检索，不要一次性加载全部工具。
流程：
1. 根据用户任务，调用 tool_search(query=任务关键词) 检索候选工具；
2. 只对命中的候选工具调用 defer_loading 加载其参数 schema；
3. 选最贴切的一个执行，参数严格匹配 schema 的 required 字段。
原则：检索 query 用「动作+对象」，例如「发送邮件」「查询天气」，不要用整句。
```

### 模板 2：工具库 JSON 条目（填配置即可跑）

```json
{"name": "send_email", "summary": "发送电子邮件给指定收件人",
 "tags": ["email", "communication"],
 "parameters": {"type": "object",
   "properties": {"to": {"type": "string"}, "subject": {"type": "string"}},
   "required": ["to", "subject"]},
 "adapter": "function", "adapter_config": {"name": "send_email"}}
```

### 模板 3：配置片段（config.yaml）

```yaml
retrieval:
  top_k: 5
  backend: hybrid
  hybrid_weight: 0.5
budget:
  context_limit: 12000
  safety_factor: 0.9
```

## 五、踩坑与解法

| 坑 | 解法 |
|---|---|
| 中文量词/虚词导致跨工具误匹配 | 分词前加停用字表（本仓库 tokenizer 已内置） |
| 工具名不带动作动词，重排失效 | `send_email` 而非 `email`，重排器对名字命中强 boost |
| defer 省得没想象中多 | defer 只省 schema；要"省 90%"得上检索模式（连 stub 都不常驻） |
| 预算卡太死，agent 反复加载反而更贵 | `safety_factor` 先给 0.9，再按实测收紧 |
| 用英文关键词搜中文工具搜不到 | 同义词要写进 summary/tags（如 calculator 写"计算/相加"） |

## 六、一键验证

```bash
git clone https://github.com/huzjie/lazyforge.git && cd lazyforge
python -m lazyforge doctor      # 检索/预算/上下文/执行/评测 全链路
```

60 工具场景实测：检索命中率 100%，上下文成本降 **94%**。换你自己的工具库，把 `library.path` 指到你的
JSON/YAML 即可。
