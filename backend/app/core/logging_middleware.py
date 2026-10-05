"""结构化访问日志中间件：记录 method/path/status/耗时/异常，并上报指标。"""
from __future__ import annotations

import time
import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.metrics import metrics

_SKIP = {"/api/metrics", "/api/health", "/docs", "/openapi.json", "/redoc"}


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _SKIP:
            return await call_next(request)
        start = time.time()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            return response
        except Exception:  # noqa: BLE001
            status = 500
            traceback.print_exc()
            raise
        finally:
            duration_ms = (time.time() - start) * 1000
            metrics.record(request.url.path, status, duration_ms)
            print(
                f'[ACCESS] {request.method} {request.url.path} '
                f'status={status} {duration_ms:.1f}ms',
                flush=True,
            )
