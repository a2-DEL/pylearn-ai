"""进程内指标：请求数 / 耗时 / 异常计数（可选 Prometheus 文本导出）。"""
from __future__ import annotations

import threading
from collections import defaultdict


class Metrics:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.total = 0
        self.errors = 0
        self.ratelimit = 0
        self.latency_sum = 0.0
        self.latency_max = 0.0
        self.by_path: dict[str, int] = defaultdict(int)
        self.error_by_path: dict[str, int] = defaultdict(int)

    def record(self, path: str, status: int, duration_ms: float) -> None:
        with self._lock:
            self.total += 1
            self.latency_sum += duration_ms
            if duration_ms > self.latency_max:
                self.latency_max = duration_ms
            self.by_path[path] += 1
            if status >= 500:
                self.errors += 1
                self.error_by_path[path] += 1

    def record_ratelimit(self) -> None:
        """限流触发计数（供 Prometheus / 看板展示）。"""
        with self._lock:
            self.ratelimit += 1

    def snapshot(self) -> dict:
        with self._lock:
            avg = (self.latency_sum / self.total) if self.total else 0.0
            return {
                "total": self.total,
                "errors": self.errors,
                "avg_latency_ms": round(avg, 2),
                "by_path": dict(self.by_path),
                "error_by_path": dict(self.error_by_path),
            }

    def prometheus(self) -> str:
        with self._lock:
            avg = (self.latency_sum / self.total) if self.total else 0.0
            lines = [
                "# HELP pylearn_requests_total 总请求数",
                "# TYPE pylearn_requests_total counter",
                f"pylearn_requests_total {self.total}",
                "# HELP pylearn_errors_total 5xx 错误数",
                "# TYPE pylearn_errors_total counter",
                f"pylearn_errors_total {self.errors}",
                "# HELP pylearn_ratelimit_total AI 限流触发次数",
                "# TYPE pylearn_ratelimit_total counter",
                f"pylearn_ratelimit_total {self.ratelimit}",
                "# HELP pylearn_latency_avg_ms 平均响应耗时(ms)",
                "# TYPE pylearn_latency_avg_ms gauge",
                f"pylearn_latency_avg_ms {round(avg, 2)}",
                "# HELP pylearn_latency_max_ms 最大响应耗时(ms)",
                "# TYPE pylearn_latency_max_ms gauge",
                f"pylearn_latency_max_ms {round(self.latency_max, 2)}",
            ]
            return "\n".join(lines) + "\n"


metrics = Metrics()
