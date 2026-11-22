"""dataset —— 评测数据集：任务 + 闭式真值（ground-truth 相关工具 id）。

真值是「闭式」的：每个任务明确列出应命中的工具 id，无需人工标注、无需
调用大模型，即可确定性地判定检索是否正确 —— 这是「可验证 reward」的来源。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    query: str
    relevant_ids: list[str]
    tag: str = ""


def build_default_dataset() -> list[Task]:
    """内置评测集：覆盖常见 agent 任务，用于 doctor / benchmark 冒烟。

    真值（relevant_ids）对齐内置 60 工具库的「最贴切工具」，每个任务唯一最优。
    """
    return [
        Task("给客户发一封项目周报邮件", ["send_email"], "communication"),
        Task("查询今天北京的天气", ["get_weather"], "info"),
        Task("把一段英文翻译成中文", ["translate_text"], "nlp"),
        Task("计算两个数字相加的结果", ["calculator"], "math"),
        Task("搜索网页上关于大模型的最新新闻", ["search_news"], "search"),
        Task("创建一个待办事项提醒", ["create_todo"], "productivity"),
        Task("读取本地文件的文本内容", ["read_file"], "fs"),
        Task("往数据库里写入一条记录", ["insert_record"], "data"),
        Task("生成一张流程图", ["generate_diagram"], "creative"),
        Task("查看当前服务器 CPU 和内存占用", ["get_system_stats"], "ops"),
    ]
