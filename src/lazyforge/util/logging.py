"""logging —— 极简日志：标准库 logging 的一层薄封装。"""
from __future__ import annotations

import logging
import sys
from enum import IntEnum


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR


_configured = False


def get_logger(name: str = "lazyforge", level: LogLevel = LogLevel.INFO) -> logging.Logger:
    global _configured
    logger = logging.getLogger(name)
    if not _configured:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)s [%(name)s] %(message)s", "%H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(int(level))
        logger.propagate = False
        _configured = True
    return logger
