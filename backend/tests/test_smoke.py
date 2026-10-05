"""冒烟测试：校验应用可导入、路由已注册、健康检查可用。"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


def _all_paths() -> set[str]:
    """从 OpenAPI schema 提取所有注册路径，最可靠。"""
    return set(app.openapi()["paths"].keys())


def test_app_imports():
    assert app is not None


def test_routes_registered():
    paths = _all_paths()
    for expected in (
        "/api/health",
        "/api/metrics",
        "/api/ai/review",
        "/api/ai/tutor",
        "/api/mistakes",
        "/api/learning-path",
        "/api/rank",
        "/api/works",
        "/api/peer-reviews",
        "/api/checkin",
        "/api/badges",
        "/api/plugins",
        # 本次新增
        "/api/plans/debug-train",
        "/api/learning-advisor",
    ):
        assert expected in paths, f"缺少路由: {expected}"


def test_health_ok():
    with TestClient(app) as client:
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["code"] == 0


@pytest.mark.asyncio
async def test_metrics_snapshot():
    from app.core.metrics import metrics

    metrics.record("/api/health", 200, 1.0)
    snap = metrics.snapshot()
    assert snap["total"] >= 1
