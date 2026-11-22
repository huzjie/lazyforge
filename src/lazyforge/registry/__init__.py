"""registry — 工具注册表：常驻 stub、延迟加载完整定义。"""
from .tool import Tool, ToolStub, ParameterSpec
from .registry import ToolRegistry
from .loader import DeferredLoader, Loader
from .library import build_tool_from_dict, build_tools_from_list, load_library
from .demo import build_demo_tools, build_large_demo_tools

__all__ = ["Tool", "ToolStub", "ParameterSpec", "ToolRegistry", "DeferredLoader",
           "Loader", "build_tool_from_dict", "build_tools_from_list", "load_library",
           "build_demo_tools", "build_large_demo_tools"]
