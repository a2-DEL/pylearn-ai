"""AI 调用限流：可插拔双后端。

- 配置 ``REDIS_URL`` 后启用 **Redis 滑动窗口限流**，多副本间统一计数，生产推荐。
- 未配置 ``REDIS_URL`` 时回退 **进程内内存限流**（单副本 / 本地开发），行为不变。

限制维度：按用户 ID 优先；游客或未登录回退到客户端 IP。
超出上限抛出 ``AppError(code=429)``，并上报限流指标。
"""
from __future__ import annotations

import time
import uuid
from collections import defaultdict
from typing import Optional

from fastapi import Request

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.metrics import metrics
from app.core.security import decode_access_token

_DAY_FMT = "%Y-%m-%d"
_DAY_WINDOW = 86_400  # 秒
_MIN_WINDOW = 60       # 秒


def _ident_from_request(request: Request) -> str:
    """优先用 Bearer 中的用户标识，否则回退客户端 IP。"""
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        payload = decode_access_token(auth[7:].strip())
        if payload and payload.get("sub"):
            return f"u:{payload['sub']}"
    return request.client.host if request.client else "unknown"


class RateLimiter:
    """限流后端抽象：子类实现 ``check``。"""

    async def check(self, ident: str) -> None:  # pragma: no cover - 抽象
        raise NotImplementedError


class MemoryRateLimiter(RateLimiter):
    """进程内内存限流（单副本）。滑动窗口实现。"""

    def __init__(self, per_min: int, per_day: int) -> None:
        self.per_min = per_min
        self.per_day = per_day
        self.min_hits: dict[str, list[float]] = defaultdict(list)
        self.day_hits: dict[str, list[float]] = defaultdict(list)
        self.today: str = ""

    def _rollover_day(self) -> None:
        day = time.strftime(_DAY_FMT)
        if day != self.today:
            self.today = day
            self.day_hits.clear()

    async def check(self, ident: str) -> None:
        self._rollover_day()
        now = time.time()

        min_hits = self.min_hits[ident]
        while min_hits and now - min_hits[0] >= _MIN_WINDOW:
            min_hits.pop(0)
        if len(min_hits) >= self.per_min:
            metrics.record_ratelimit()
            raise AppError("请求过于频繁，请稍后再试（每分钟上限）", code=429)
        min_hits.append(now)

        day_hits = self.day_hits[ident]
        while day_hits and now - day_hits[0] >= _DAY_WINDOW:
            day_hits.pop(0)
        if len(day_hits) >= self.per_day:
            metrics.record_ratelimit()
            raise AppError("今日 AI 调用次数已达上限", code=429)
        day_hits.append(now)


class RedisRateLimiter(RateLimiter):
    """Redis 滑动窗口限流（多副本安全）。

    每个窗口用一个 ZSET 记录时间戳：ZREMRANGEBYSSCORE 清理过期项，
    ZADD 写入当前时间戳，ZCARD 取当前窗口内计数，EXPIRE 兜底回收键。
    """

    def __init__(self, redis_client, per_min: int, per_day: int) -> None:
        self.redis = redis_client
        self.per_min = per_min
        self.per_day = per_day

    async def _sliding(self, ident: str, window: str, now: float, span: int, limit: int) -> None:
        key = f"pylearn:ratelimit:{window}:{ident}"
        member = f"{now}:{uuid.uuid4().hex}"
        async with self.redis.pipeline() as pipe:
            pipe.zremrangebyscore(key, 0, now - span)
            pipe.zadd(key, {member: now})
            pipe.expire(key, span + 1)
            pipe.zcard(key)
            results = await pipe.execute()
        count = results[3]
        if count > limit:
            metrics.record_ratelimit()
            msg = "请求过于频繁，请稍后再试（每分钟上限）" if window == "min" \
                else "今日 AI 调用次数已达上限"
            raise AppError(msg, code=429)

    async def check(self, ident: str) -> None:
        now = time.time()
        await self._sliding(ident, "min", now, _MIN_WINDOW, self.per_min)
        await self._sliding(ident, "day", now, _DAY_WINDOW, self.per_day)


_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """依据 ``REDIS_URL`` 返回 Redis 或内存限流实例（惰性单例）。"""
    global _limiter
    if _limiter is not None:
        return _limiter
    if settings.REDIS_URL:
        try:
            from redis.asyncio import Redis

            client = Redis.from_url(settings.REDIS_URL, decode_responses=False)
            _limiter = RedisRateLimiter(client, settings.AI_RATE_PER_MIN, settings.AI_RATE_PER_DAY)
        except Exception:  # noqa: BLE001 - Redis 不可用回退内存
            _limiter = MemoryRateLimiter(settings.AI_RATE_PER_MIN, settings.AI_RATE_PER_DAY)
    else:
        _limiter = MemoryRateLimiter(settings.AI_RATE_PER_MIN, settings.AI_RATE_PER_DAY)
    return _limiter


async def check_ai_rate(request: Request) -> None:
    """按用户优先、回退 IP 的 AI 调用限流检查（异步）。"""
    ident = _ident_from_request(request)
    await get_rate_limiter().check(ident)
