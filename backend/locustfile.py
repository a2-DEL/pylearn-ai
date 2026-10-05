"""Locust 压测示例：对核心只读端点做并发探测。

运行：locust -f locustfile.py --host http://127.0.0.1:8000
"""
from __future__ import annotations

from locust import HttpUser, between, task


class PyLearnUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(3)
    def health(self):
        self.client.get("/api/health")

    @task(2)
    def metrics(self):
        self.client.get("/api/metrics")

    @task(1)
    def knowledge(self):
        self.client.get("/api/knowledge")
