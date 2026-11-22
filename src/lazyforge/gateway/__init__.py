"""gateway —— 检索 -> 延迟加载 -> 分发执行 的一站式入口。"""
from .gateway import LazyGateway, GatewayPlan
from .context import ContextAssembler
from .dispatcher import Dispatcher

__all__ = ["LazyGateway", "GatewayPlan", "ContextAssembler", "Dispatcher"]
