# API 参考

## 快速开始

```python
from lazyforge.config import Config
from lazyforge.gateway.gateway import LazyGateway
from lazyforge.registry import build_demo_tools

gw = LazyGateway.from_tools(build_demo_tools(), Config())

# 规划：检索 + 预算 + 上下文
plan = gw.plan("给客户发一封项目周报邮件", top_k=3)
print(plan.savings_ratio)          # 上下文节省比例
print([d.stub.name for d in plan.decisions])  # 已加载 schema 的工具

# 执行：检索最相关工具并调用
result = gw.run("发送邮件", {"to": "a@b.com", "subject": "hi", "body": "..."})
```

## 核心类

### LazyGateway
- `from_tools(tools, config=None)` — 从 Tool 列表构建网关并建索引
- `register(tool)` / `register_many(tools)` — 注册工具
- `build_index()` — 建检索索引
- `plan(task, top_k=None)` → `GatewayPlan` — 检索 + 预算 + 上下文
- `run(task, args, top_k=1)` → `ToolResult` — 检索并执行

### GatewayPlan
- `ranked` — 检索排序结果（ScoredTool 列表）
- `decisions` — 加载/延迟决策（LoadDecision 列表）
- `context` — 组装后的上下文（tools + stats）
- `full_cost` / `lazy_cost` — 全量 vs 按需 token 成本
- `savings_ratio` — 节省比例

### ToolRegistry / ToolStub / Tool
- `ToolStub`：常驻轻量条目（name / summary / tags / ref / adapter）
- `Tool`：完整定义（description / parameters JSON Schema / examples）
- `ToolRegistry.register(tool)` — 注册，自动拆 stub

### 适配器
- `FunctionAdapter` — 本地函数（`register_function` 装饰器或 registry 传入）
- `HttpAdapter` — REST 调用（`adapter_config.url/method/headers`）
- `CliAdapter` — 子进程（`adapter_config.command/args`）
- `McpAdapter` — MCP（`adapter_config.endpoint` + transport）

## 从 JSON/YAML 加载工具库

```python
from lazyforge.registry import load_library
tools = load_library("examples/tools.json")
```

## CLI

```
python -m lazyforge doctor                 # 一键冒烟
python -m lazyforge search "发邮件" -k 3   # 检索
python -m lazyforge plan   "发邮件"        # 检索 + 预算 + 上下文
python -m lazyforge run    "发邮件"        # 检索并执行（mock）
python -m lazyforge benchmark              # 评测报告
```
