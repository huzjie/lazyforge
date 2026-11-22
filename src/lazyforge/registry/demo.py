"""demo —— 内置演示工具库：构建 12 个覆盖多领域的示例工具。

doctor 命令用这批工具冒烟：检索、预算、上下文组装、执行全链路各跑一遍。
真实项目替换为你的工具 JSON/YAML 即可。
"""
from __future__ import annotations

from .library import build_tool_from_dict

_DEMO: list[dict] = [
    {"name": "send_email", "summary": "发送电子邮件给指定收件人", "tags": ["email", "communication", "mail"],
     "parameters": {"type": "object", "properties": {
         "to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
         "required": ["to", "subject", "body"]},
     "adapter": "function", "adapter_config": {"name": "send_email"}},
    {"name": "get_weather", "summary": "查询指定城市的天气", "tags": ["weather", "info", "query"],
     "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
     "adapter": "function", "adapter_config": {"name": "get_weather"}},
    {"name": "translate_text", "summary": "把文本从一种语言翻译成另一种", "tags": ["translate", "nlp", "language"],
     "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "target_lang": {"type": "string"}},
                    "required": ["text", "target_lang"]},
     "adapter": "function", "adapter_config": {"name": "translate_text"}},
    {"name": "calculator", "summary": "执行数学计算：加减乘除、四则运算求值、两个数字相加", "tags": ["math", "calc", "arithmetic", "计算", "运算", "相加"],
     "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]},
     "adapter": "function", "adapter_config": {"name": "calculator"}},
    {"name": "web_search", "summary": "搜索网页获取最新信息", "tags": ["search", "web", "browse"],
     "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
     "adapter": "function", "adapter_config": {"name": "web_search"}},
    {"name": "create_todo", "summary": "创建一条待办事项", "tags": ["todo", "task", "productivity"],
     "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "due": {"type": "string"}},
                    "required": ["title"]},
     "adapter": "function", "adapter_config": {"name": "create_todo"}},
    {"name": "read_file", "summary": "读取本地文本文件内容", "tags": ["file", "fs", "io", "read"],
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
     "adapter": "function", "adapter_config": {"name": "read_file"}},
    {"name": "db_query", "summary": "对数据库执行查询并返回结果", "tags": ["database", "sql", "data", "query"],
     "parameters": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]},
     "adapter": "function", "adapter_config": {"name": "db_query"}},
    {"name": "generate_diagram", "summary": "根据描述生成流程图或示意图", "tags": ["diagram", "creative", "image", "visual"],
     "parameters": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]},
     "adapter": "function", "adapter_config": {"name": "generate_diagram"}},
    {"name": "get_system_stats", "summary": "查看服务器 CPU 与内存占用", "tags": ["system", "ops", "monitor", "cpu", "memory"],
     "parameters": {"type": "object", "properties": {}},
     "adapter": "function", "adapter_config": {"name": "get_system_stats"}},
    {"name": "schedule_meeting", "summary": "安排一场会议并发送邀请", "tags": ["calendar", "meeting", "schedule"],
     "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "time": {"type": "string"},
                    "attendees": {"type": "array"}}, "required": ["title", "time"]},
     "adapter": "function", "adapter_config": {"name": "schedule_meeting"}},
    {"name": "analyze_data", "summary": "对结构化数据做统计分析", "tags": ["data", "analysis", "statistics", "analytics"],
     "parameters": {"type": "object", "properties": {"dataset": {"type": "string"}, "metric": {"type": "string"}},
                    "required": ["dataset"]},
     "adapter": "function", "adapter_config": {"name": "analyze_data"}},
]


def build_demo_tools() -> list:
    """返回 12 个演示工具，供 doctor / demo / benchmark 使用。"""
    return [build_tool_from_dict(r) for r in _DEMO]


# 扩展领域工具：把「工具库」撑到 60 个，演示检索 + 节省在规模下的价值
_MORE: list[dict] = [
    # 通讯 / 协作
    {"name": "send_slack", "summary": "发送 Slack 频道消息", "tags": ["slack", "im", "communication"], "parameters": {"type": "object", "properties": {"channel": {"type": "string"}, "text": {"type": "string"}}, "required": ["channel", "text"]}},
    {"name": "send_wechat", "summary": "通过企业微信发送消息", "tags": ["wechat", "im", "communication"], "parameters": {"type": "object", "properties": {"to": {"type": "string"}, "text": {"type": "string"}}, "required": ["to", "text"]}},
    {"name": "post_comment", "summary": "在工单或文章下发表评论", "tags": ["comment", "ticket", "communication"], "parameters": {"type": "object", "properties": {"target": {"type": "string"}, "body": {"type": "string"}}, "required": ["target", "body"]}},
    {"name": "create_channel", "summary": "创建一个新的讨论频道", "tags": ["channel", "team", "communication"], "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    # 文件 / 存储
    {"name": "write_file", "summary": "写入文本内容到本地文件", "tags": ["file", "fs", "write"], "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "list_files", "summary": "列出目录下的文件列表", "tags": ["file", "fs", "ls", "dir"], "parameters": {"type": "object", "properties": {"dir": {"type": "string"}}, "required": ["dir"]}},
    {"name": "delete_file", "summary": "删除指定文件", "tags": ["file", "fs", "delete"], "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "upload_file", "summary": "上传文件到对象存储", "tags": ["upload", "storage", "s3", "oss"], "parameters": {"type": "object", "properties": {"local": {"type": "string"}, "remote": {"type": "string"}}, "required": ["local", "remote"]}},
    {"name": "download_file", "summary": "从 URL 下载文件到本地", "tags": ["download", "http", "file"], "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "dest": {"type": "string"}}, "required": ["url"]}},
    # 数据 / 数据库
    {"name": "insert_record", "summary": "向数据表插入一条记录", "tags": ["database", "sql", "insert"], "parameters": {"type": "object", "properties": {"table": {"type": "string"}, "row": {"type": "object"}}, "required": ["table", "row"]}},
    {"name": "update_record", "summary": "更新数据表的一条记录", "tags": ["database", "sql", "update"], "parameters": {"type": "object", "properties": {"table": {"type": "string"}, "where": {"type": "string"}, "row": {"type": "object"}}, "required": ["table"]}},
    {"name": "export_csv", "summary": "把查询结果导出为 CSV 文件", "tags": ["data", "csv", "export"], "parameters": {"type": "object", "properties": {"sql": {"type": "string"}, "path": {"type": "string"}}, "required": ["sql", "path"]}},
    {"name": "get_schema", "summary": "查看数据表的表结构", "tags": ["database", "schema", "ddl"], "parameters": {"type": "object", "properties": {"table": {"type": "string"}}, "required": ["table"]}},
    # Web / 检索
    {"name": "fetch_url", "summary": "抓取网页的 HTML 内容", "tags": ["http", "web", "fetch", "scrape"], "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
    {"name": "search_news", "summary": "搜索最新新闻资讯", "tags": ["news", "search", "web"], "parameters": {"type": "object", "properties": {"keyword": {"type": "string"}, "days": {"type": "integer"}}, "required": ["keyword"]}},
    {"name": "get_stock_price", "summary": "查询股票实时价格", "tags": ["stock", "finance", "price", "quote"], "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}},
    # NLP
    {"name": "summarize_text", "summary": "把长文本摘要成要点", "tags": ["nlp", "summarize", "summary"], "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "sentiment_analysis", "summary": "分析文本的情感倾向", "tags": ["nlp", "sentiment", "emotion"], "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "extract_entities", "summary": "从文本抽取命名实体", "tags": ["nlp", "ner", "entity"], "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "generate_image", "summary": "根据提示词生成图片", "tags": ["image", "generate", "diffusion", "creative"], "parameters": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}},
    # 运维 / 监控
    {"name": "restart_service", "summary": "重启指定的服务进程", "tags": ["ops", "service", "restart"], "parameters": {"type": "object", "properties": {"service": {"type": "string"}}, "required": ["service"]}},
    {"name": "check_logs", "summary": "查看服务最近日志", "tags": ["ops", "log", "monitor"], "parameters": {"type": "object", "properties": {"service": {"type": "string"}, "lines": {"type": "integer"}}, "required": ["service"]}},
    {"name": "get_disk_usage", "summary": "查看磁盘空间占用", "tags": ["ops", "disk", "storage", "monitor"], "parameters": {"type": "object", "properties": {}}},
    {"name": "run_sql_backup", "summary": "执行数据库备份", "tags": ["ops", "backup", "database"], "parameters": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}},
    # 生产力
    {"name": "create_reminder", "summary": "创建一个定时提醒", "tags": ["reminder", "productivity", "todo"], "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "at": {"type": "string"}}, "required": ["text", "at"]}},
    {"name": "update_todo", "summary": "更新待办事项状态", "tags": ["todo", "task", "update"], "parameters": {"type": "object", "properties": {"id": {"type": "string"}, "done": {"type": "boolean"}}, "required": ["id"]}},
    {"name": "search_knowledge", "summary": "搜索知识库文档", "tags": ["knowledge", "search", "kb", "doc"], "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "create_document", "summary": "创建一篇在线文档", "tags": ["document", "doc", "create"], "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "body": {"type": "string"}}, "required": ["title"]}},
    # 财务 / 业务
    {"name": "calc_currency", "summary": "货币汇率换算", "tags": ["finance", "currency", "exchange", "convert"], "parameters": {"type": "object", "properties": {"amount": {"type": "number"}, "from": {"type": "string"}, "to": {"type": "string"}}, "required": ["amount", "from", "to"]}},
    {"name": "generate_invoice", "summary": "生成一张发票", "tags": ["finance", "invoice", "billing"], "parameters": {"type": "object", "properties": {"customer": {"type": "string"}, "amount": {"type": "number"}}, "required": ["customer", "amount"]}},
    {"name": "check_order_status", "summary": "查询订单状态", "tags": ["order", "business", "ecommerce"], "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]}},
    {"name": "refund_order", "summary": "对订单发起退款", "tags": ["order", "refund", "business"], "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}}, "required": ["order_id"]}},
    # 时间 / 地理
    {"name": "get_current_time", "summary": "获取当前时间", "tags": ["time", "clock", "date"], "parameters": {"type": "object", "properties": {"tz": {"type": "string"}}}},
    {"name": "geocode", "summary": "把地址解析为经纬度", "tags": ["geo", "map", "location", "geocode"], "parameters": {"type": "object", "properties": {"address": {"type": "string"}}, "required": ["address"]}},
    {"name": "get_distance", "summary": "计算两地之间的距离", "tags": ["geo", "map", "distance", "route"], "parameters": {"type": "object", "properties": {"from": {"type": "string"}, "to": {"type": "string"}}, "required": ["from", "to"]}},
    {"name": "translate_doc", "summary": "翻译整篇文档并保留格式", "tags": ["translate", "document", "nlp"], "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "lang": {"type": "string"}}, "required": ["path", "lang"]}},
    # 内容 / 媒体
    {"name": "transcribe_audio", "summary": "把音频转写为文字", "tags": ["audio", "asr", "transcribe", "speech"], "parameters": {"type": "object", "properties": {"file": {"type": "string"}}, "required": ["file"]}},
    {"name": "generate_video", "summary": "根据提示词生成短视频", "tags": ["video", "generate", "creative"], "parameters": {"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]}},
    {"name": "ocr_image", "summary": "识别图片中的文字", "tags": ["ocr", "image", "vision"], "parameters": {"type": "object", "properties": {"image": {"type": "string"}}, "required": ["image"]}},
    {"name": "resize_image", "summary": "调整图片尺寸", "tags": ["image", "resize", "edit"], "parameters": {"type": "object", "properties": {"image": {"type": "string"}, "width": {"type": "integer"}, "height": {"type": "integer"}}, "required": ["image"]}},
    # 安全 / 权限
    {"name": "check_permission", "summary": "检查用户对资源的权限", "tags": ["auth", "permission", "security", "acl"], "parameters": {"type": "object", "properties": {"user": {"type": "string"}, "resource": {"type": "string"}}, "required": ["user", "resource"]}},
    {"name": "encrypt_text", "summary": "对文本进行加密", "tags": ["security", "encrypt", "crypto"], "parameters": {"type": "object", "properties": {"text": {"type": "string"}, "key": {"type": "string"}}, "required": ["text"]}},
    {"name": "audit_log", "summary": "写入一条审计日志", "tags": ["security", "audit", "log"], "parameters": {"type": "object", "properties": {"event": {"type": "string"}, "user": {"type": "string"}}, "required": ["event"]}},
    # 报告 / 分析
    {"name": "generate_report", "summary": "根据数据生成分析报告", "tags": ["report", "analysis", "document"], "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "data": {"type": "object"}}, "required": ["title"]}},
    {"name": "make_chart", "summary": "把数据渲染成图表", "tags": ["chart", "visual", "data", "plot"], "parameters": {"type": "object", "properties": {"data": {"type": "array"}, "type": {"type": "string"}}, "required": ["data"]}},
    {"name": "train_model", "summary": "训练一个机器学习模型", "tags": ["ml", "train", "model"], "parameters": {"type": "object", "properties": {"dataset": {"type": "string"}, "target": {"type": "string"}}, "required": ["dataset", "target"]}},
    {"name": "predict", "summary": "用模型做一次推理预测", "tags": ["ml", "predict", "inference"], "parameters": {"type": "object", "properties": {"model": {"type": "string"}, "input": {"type": "object"}}, "required": ["model"]}},
    {"name": "optimize_sql", "summary": "分析并优化 SQL 查询", "tags": ["database", "sql", "optimize", "perf"], "parameters": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}},
    {"name": "monitor_agent", "summary": "监控智能体运行状态", "tags": ["agent", "monitor", "ops", "observe"], "parameters": {"type": "object", "properties": {"agent_id": {"type": "string"}}, "required": ["agent_id"]}},
]


def build_large_demo_tools() -> list:
    """返回 60 个演示工具（12 基础 + 48 扩展），演示规模下的检索与节省。"""
    return [build_tool_from_dict(r) for r in _DEMO + _MORE]
