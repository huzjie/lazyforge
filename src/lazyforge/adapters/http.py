"""http —— HTTP 工具适配器：把工具映射到 REST 端点调用。

adapter_config 约定：
- url: 模板 URL（支持 {param} 占位符，从 args 填充）
- method: GET / POST / PUT / DELETE（默认 POST）
- headers: 额外请求头
- timeout: 秒（默认 10）
纯标准库 urllib，不引入 requests。
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

from .base import ToolAdapter, ToolResult


class HttpAdapter(ToolAdapter):
    name = "http"

    def _fill_url(self, url: str, args: dict[str, Any]) -> str:
        out = url
        for k, v in args.items():
            out = out.replace("{" + k + "}", str(v))
        return out

    def invoke(self, tool: Any, args: dict[str, Any]) -> ToolResult:
        start = time.perf_counter()
        cfg = tool.adapter_config or {}
        url = cfg.get("url", "")
        method = cfg.get("method", "POST").upper()
        timeout = cfg.get("timeout", 10)
        try:
            data = None
            if method in ("POST", "PUT"):
                data = json.dumps(args).encode("utf-8")
            elif args:
                # GET/DELETE：参数拼 query string
                qs = "&".join(f"{k}={v}" for k, v in args.items())
                url = url + ("&" if "?" in url else "?") + qs
            req = urllib.request.Request(
                self._fill_url(url, args),
                data=data,
                method=method,
                headers={"Content-Type": "application/json",
                         **(cfg.get("headers") or {})},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                latency = (time.perf_counter() - start) * 1000
                try:
                    parsed = json.loads(body)
                except json.JSONDecodeError:
                    parsed = body
                return ToolResult.success(parsed, latency_ms=latency,
                                          status=resp.status)
        except urllib.error.HTTPError as exc:
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.failure(f"HTTP {exc.code}: {exc.reason}",
                                      latency_ms=latency)
        except Exception as exc:  # noqa: BLE001
            latency = (time.perf_counter() - start) * 1000
            return ToolResult.failure(str(exc), latency_ms=latency)
