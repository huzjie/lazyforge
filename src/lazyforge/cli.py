"""cli —— 命令行入口。核心命令：

- doctor    一键冒烟：检索 / 预算 / 上下文 / 执行 / 评测全链路跑通
- search    <query>  检索最相关工具
- plan      <query>  展示检索 + 预算 + 上下文组装结果
- run       <query>  检索并执行最相关工具（演示用 mock 实现）
- benchmark 跑内置数据集评测并输出报告
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from . import __version__
from .config import Config
from .eval.benchmark import benchmark
from .eval.dataset import build_default_dataset
from .gateway.gateway import LazyGateway
from .registry.demo import build_large_demo_tools
from .registry.library import load_library
from .util.jsonutil import dumps


def _build_gateway(config: Config) -> LazyGateway:
    gw = LazyGateway(config)
    # 优先读配置里的工具库文件，否则用内置 60 工具演示库
    lib_path = os.environ.get("LAZYFORGE_LIBRARY") or config.library.path
    if lib_path:
        try:
            tools = load_library(lib_path)
        except (FileNotFoundError, RuntimeError, IsADirectoryError,
                json.JSONDecodeError):
            tools = build_large_demo_tools()
    else:
        tools = build_large_demo_tools()
    gw.register_many(tools)
    gw.build_index()
    return gw


def _demo_callables() -> dict[str, Any]:
    """演示用 mock 函数，让 run 命令能真实返回结果。"""
    return {
        "send_email": lambda **kw: f"已发送邮件 -> {kw.get('to')}",
        "get_weather": lambda **kw: f"{kw.get('city')} 晴 22℃",
        "calculator": lambda **kw: f"{kw.get('expression')} = 42",
        "translate_text": lambda **kw: f"[{kw.get('target_lang')}] {kw.get('text')}",
        "web_search": lambda **kw: f"关于「{kw.get('query')}」的搜索结果…",
        "create_todo": lambda **kw: f"已创建待办: {kw.get('title')}",
        "read_file": lambda **kw: f"<{kw.get('path')}> 内容…",
        "db_query": lambda **kw: "[{('id':1,'name':'demo')}]",
        "generate_diagram": lambda **kw: f"已生成「{kw.get('prompt')}」示意图",
        "get_system_stats": lambda **kw: "CPU 32% / Mem 61%",
        "schedule_meeting": lambda **kw: f"会议「{kw.get('title')}」已安排",
        "analyze_data": lambda **kw: f"「{kw.get('dataset')}」均值=3.14",
    }


def _doctor(config: Config) -> int:
    gw = _build_gateway(config)
    print(f"lazyforge v{__version__} · 工具数={len(gw.registry)}")

    # 1) 检索冒烟
    ranked = gw.searcher.search("给客户发一封项目周报邮件", top_k=3)
    top = ranked[0].stub.name
    print(f"[检索] '给客户发邮件' -> top1={top}")
    assert top == "send_email", f"检索错误: {top}"

    # 2) 预算 + 上下文
    plan = gw.plan("给客户发一封项目周报邮件", top_k=3)
    print(f"[预算] 全量={plan.full_cost} token, defer_loading={plan.lazy_cost} token "
          f"(省 {plan.savings_ratio:.1%}), 检索模式={plan.retrieval_cost} token "
          f"(省 {plan.retrieval_savings_ratio:.1%})")
    assert plan.lazy_cost < plan.full_cost, "按需加载未节省上下文"
    print(f"[上下文] 已加载 schema 的工具: {[d.stub.name for d in plan.decisions]}")

    # 3) 执行（mock）
    from .gateway.dispatcher import Dispatcher
    from .adapters.function import FunctionAdapter
    adapter = FunctionAdapter(_demo_callables())
    gw.dispatcher._adapters["function"] = adapter  # noqa: SLF001
    result = gw.run("发送邮件", {"to": "a@b.com", "subject": "周报", "body": "内容"})
    assert result.ok, result.error
    print(f"[执行] {result.output}")

    # 4) 评测
    report = benchmark(gw, build_default_dataset())
    print(f"[评测] recall@k={report.avg_recall:.2f} mrr={report.avg_mrr:.2f} "
          f"skill={report.avg_skill:.2f} hit_rate={report.hit_rate:.2f}")
    assert report.avg_skill >= 0.9, f"skill 未收敛: {report.avg_skill}"

    print("\n✅ doctor 通过：检索 / 预算 / 上下文 / 执行 / 评测 全链路正常")
    return 0


def _cmd_search(gw: LazyGateway, query: str, top_k: int) -> int:
    for r in gw.searcher.search(query, top_k=top_k):
        print(f"  #{r.rank+1} {r.stub.name}  (score={r.score:.4f})  {r.stub.summary}")
    return 0


def _cmd_plan(gw: LazyGateway, query: str, top_k: int) -> int:
    plan = gw.plan(query, top_k=top_k)
    print(dumps({"task": query, "full_cost": plan.full_cost,
                 "lazy_cost": plan.lazy_cost,
                 "savings_ratio": round(plan.savings_ratio, 4),
                 "loaded": [d.stub.name for d in plan.decisions],
                 "context_stats": plan.context["stats"]}))
    return 0


def _cmd_run(gw: LazyGateway, query: str) -> int:
    from .adapters.function import FunctionAdapter
    gw.dispatcher._adapters["function"] = FunctionAdapter(_demo_callables())  # noqa: SLF001
    result = gw.run(query, {}, top_k=1)
    print(result.output if result.ok else f"❌ {result.error}")
    return 0 if result.ok else 1


def _cmd_benchmark(gw: LazyGateway) -> int:
    report = benchmark(gw, build_default_dataset())
    print(dumps(report.to_dict()))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="lazyforge",
                                 description="Agent 工具库按需检索与延迟加载网关")
    ap.add_argument("--version", action="version", version=f"lazyforge {__version__}")
    ap.add_argument("--config", default=os.environ.get("LAZYFORGE_CONFIG"))
    sub = ap.add_subparsers(dest="command")

    sub.add_parser("doctor", help="一键冒烟：全链路验证")
    p_search = sub.add_parser("search", help="检索最相关工具")
    p_search.add_argument("query")
    p_search.add_argument("-k", type=int, default=5)
    p_plan = sub.add_parser("plan", help="展示检索 + 预算 + 上下文")
    p_plan.add_argument("query")
    p_plan.add_argument("-k", type=int, default=5)
    p_run = sub.add_parser("run", help="检索并执行最相关工具（mock）")
    p_run.add_argument("query")
    sub.add_parser("benchmark", help="跑内置评测集")

    args = ap.parse_args(argv)
    config = Config.load(args.config)

    if args.command == "doctor":
        return _doctor(config)
    gw = _build_gateway(config)
    if args.command == "search":
        return _cmd_search(gw, args.query, args.k)
    if args.command == "plan":
        return _cmd_plan(gw, args.query, args.k)
    if args.command == "run":
        return _cmd_run(gw, args.query)
    if args.command == "benchmark":
        return _cmd_benchmark(gw)
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
