"""FastAPI 应用入口：CORS、路由注册、Swagger、统一异常、生命周期建表。"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.exceptions import (
    AppError,
    app_error_handler,
    unhandled_handler,
    validation_handler,
)
from app.core.logging_middleware import LoggingMiddleware
from app.core.metrics import metrics
from app.plugins import load_plugins
from app.routers import (
    ai,
    ai_config,
    auth,
    checkin,
    classes,
    knowledge,
    learning_progress,
    mistakes,
    peer_review,
    plans,
    plugins,
    problems,
    rank,
    review,
    sandbox,
    stats,
    tasks,
    works,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时建表并写入种子数据
    await init_db()
    from app.seed import seed_all

    await seed_all()
    # 扫描并加载内置/外部插件（含动态模型适配器注册）
    load_plugins()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="开源 Python 智能学习与编程训练平台（阶段三：AI陪练·竞赛社区·插件生态·生产化）",
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_handler)
app.add_exception_handler(RequestValidationError, validation_handler)

# 基础能力
app.include_router(sandbox.router, prefix="/api", tags=["sandbox"])
app.include_router(ai_config.router, prefix="/api", tags=["ai-config"])
app.include_router(problems.router, prefix="/api", tags=["problems"])
app.include_router(knowledge.router, prefix="/api", tags=["knowledge"])
app.include_router(ai.router, prefix="/api", tags=["ai"])

# 阶段二：认证 / 班级 / 任务 / 进度 / 看板 / 方案
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(classes.router, prefix="/api", tags=["classes"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(learning_progress.router, prefix="/api", tags=["learning-progress"])
app.include_router(stats.router, prefix="/api", tags=["stats"])
app.include_router(plans.router, prefix="/api", tags=["plans"])

# 阶段三：AI 陪练 / 社区 / 插件 / 可观测
app.include_router(review.router, prefix="/api", tags=["ai-review"])
app.include_router(mistakes.router, prefix="/api", tags=["mistakes"])
app.include_router(rank.router, prefix="/api", tags=["rank"])
app.include_router(works.router, prefix="/api", tags=["works"])
app.include_router(peer_review.router, prefix="/api", tags=["peer-review"])
app.include_router(checkin.router, prefix="/api", tags=["checkin"])
app.include_router(plugins.router, prefix="/api", tags=["plugins"])


@app.get("/api/health", tags=["health"])
async def health():
    return {"code": 0, "message": "ok", "data": {"app": settings.APP_NAME, "version": "0.3.0"}}


@app.get("/api/metrics", tags=["metrics"])
async def get_metrics(request: Request):
    """基础指标：JSON 快照；若 Accept 含 text/plain 则返回 Prometheus 文本。"""
    accept = request.headers.get("Accept", "")
    if "text/plain" in accept:
        return Response(content=metrics.prometheus(), media_type="text/plain; version=0.0.4")
    return {"code": 0, "message": "ok", "data": metrics.snapshot()}
