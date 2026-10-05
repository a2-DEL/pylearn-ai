"""异步数据库引擎、会话与基类。同一套 ORM 兼容 SQLite / PostgreSQL。"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

_connect_args: dict = {}
_engine_kwargs: dict = {"echo": settings.DEBUG, "future": True, "pool_pre_ping": True}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}
    _engine_kwargs["connect_args"] = _connect_args
else:
    # PostgreSQL 等生产库：启用连接池，提升并发与复用
    _engine_kwargs["pool_size"] = 10
    _engine_kwargs["max_overflow"] = 20
    _engine_kwargs["pool_recycle"] = 1800

engine = create_async_engine(settings.DATABASE_URL, **_engine_kwargs)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """所有 ORM 模型的声明基类。"""


async def init_db() -> None:
    """建表（幂等）。阶段二前由 lifespan 调用。"""
    from app.models import models  # noqa: F401  确保模型被注册

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：获取数据库会话。"""
    async with SessionLocal() as session:
        yield session
