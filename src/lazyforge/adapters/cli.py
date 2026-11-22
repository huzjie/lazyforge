"""cli —— 命令行工具适配器：把工具映射到子进程调用。

adapter_config 约定：
- command: 命令（支持 {param} 占位符）
- args: 附加参数列表
- timeout: 秒（默认 30）
- cwd: 工作目录
适用于「把既有脚本包装成 agent 工具」的场景。
"""
from __future__ import annotations

import shlex
import subprocess
import time
from typing import Any

from .base import ToolAdapter, ToolResult


class CliAdapter(ToolAdapter):
    name = "cli"

    def invoke(self, tool: Any, args: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        cfg = tool.adapter_config or {}
        command = cfg.get("command", "")
        for k, v in args.items():
            command = command.replace("{" + k + "}", str(v))
        extra = cfg.get("args", [])
        timeout = cfg.get("timeout", 30)
        cwd = cfg.get("cwd")
        try:
            proc = subprocess.run(
                shlex.split(command) + [str(a) for a in extra],
                capture_output=True, text=True, timeout=timeout, cwd=cwd,
            )
            latency = (time.perf_counter() - start) * 1000
            if proc.returncode == 0:
                return ToolResult.success(proc.stdout.strip(), latency_ms=latency,
                                          returncode=proc.returncode)
            return ToolResult.failure(proc.stderr.strip() or "非零退出码",
                                      latency_ms=latency, returncode=proc.returncode)
        except subprocess.TimeoutExpired:
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.failure(f"超时（>{timeout}s）", latency_ms=latency)
        except Exception as exc:  # noqa: BLE001
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.failure(str(exc), latency_ms=latency)
