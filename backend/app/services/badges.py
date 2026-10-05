"""徽章发放服务：批改成功后触发，避免侵入主流程。"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Badge


async def award_badge(
    user_id: int,
    badge_type: str,
    badge_name: str,
    reason: str,
    db: AsyncSession,
) -> None:
    """同类型徽章仅发放一次（幂等）。"""
    exists = (
        await db.execute(
            select(Badge).where(Badge.user_id == user_id, Badge.badge_type == badge_type)
        )
    ).scalars().first()
    if exists:
        return
    db.add(
        Badge(
            user_id=user_id,
            badge_type=badge_type,
            badge_name=badge_name,
            reason=reason,
        )
    )
    await db.commit()


async def maybe_award_full_score(user_id: int, score: int, db: AsyncSession) -> None:
    """满分作业徽章。"""
    if score >= 100:
        await award_badge(
            user_id,
            "full_score",
            "满分作业",
            "完成一次满分提交（score=100）",
            db,
        )


async def maybe_award_streak(user_id: int, streak: int, db: AsyncSession) -> None:
    """连续打卡徽章。"""
    await award_badge(
        user_id,
        "streak",
        "坚持不懈",
        f"连续打卡 {streak} 天",
        db,
    )
