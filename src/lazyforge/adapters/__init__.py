"""adapters —— 工具执行适配器：function / http / cli / mcp 四类。"""
from .base import ToolAdapter, ToolResult
from .function import FunctionAdapter
from .http import HttpAdapter
from .cli import CliAdapter
from .mcp import McpAdapter
from .registry import get_adapter

__all__ = ["ToolAdapter", "ToolResult", "FunctionAdapter", "HttpAdapter",
           "CliAdapter", "McpAdapter", "get_adapter"]
