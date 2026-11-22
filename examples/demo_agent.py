"""demo_agent —— 一个完整的最小可运行示例：把 lazyforge 接入一个伪 Agent。

演示三步：
1. 注册工具库（换成你的 JSON/YAML 即可）
2. 对用户任务做检索 + 预算 + 上下文组装
3. 用检索出的工具执行任务

运行：python examples/demo_agent.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from lazyforge.config import Config  # noqa: E402
from lazyforge.gateway.gateway import LazyGateway  # noqa: E402
from lazyforge.registry.demo import build_demo_tools  # noqa: E402


def main() -> None:
    gw = LazyGateway.from_tools(build_demo_tools(), Config())

    task = "给客户发一封项目周报邮件"
    plan = gw.plan(task, top_k=3)

    print(f"任务: {task}")
    print(f"上下文成本: 全量 {plan.full_cost} token -> 按需 {plan.lazy_cost} token "
          f"(节省 {plan.savings_ratio:.0%})")
    print("已加载 schema 的工具:")
    for d in plan.decisions:
        print(f"  - {d.stub.name}: {d.decision.value}")
    print("检索排名:")
    for r in plan.ranked:
        print(f"  #{r.rank + 1} {r.stub.name} (score={r.score:.4f})")


if __name__ == "__main__":
    main()
