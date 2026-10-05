"""学习打卡与徽章：每日去重打卡、连续天数、徽章墙。"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Badge, Checkin, User
from app.schemas.schemas import BadgeOut, CheckinOut
from app.services.badges import award_badge, maybe_award_streak

router = APIRouter()


def _today() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


@router.post("/checkin", response_model=CheckinOut)
async def do_checkin(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = _today()
    existing = (
        await db.execute(
            select(Checkin).where(Checkin.user_id == user.id, Checkin.checkin_date == today)
        )
    ).scalars().first()
    if not existing:
        db.add(Checkin(user_id=user.id, checkin_date=today))
        await db.commit()

    # 连续天数：从今天向前数连续打卡天数
    dates = (
        await db.execute(
            select(Checkin.checkin_date).where(Checkin.user_id == user.id)
        )
    ).scalars().all()
    date_set = set(dates)
    streak = 0
    cur = datetime.utcnow().date()
    while cur.strftime("%Y-%m-%d") in date_set:
        streak += 1
        cur -= timedelta(days=1)
    total = len(date_set)

    # 连续打卡 >=7 发放徽章
    if streak >= 7:
        await maybe_award_streak(user.id, streak, db)
    return CheckinOut(date=today, streak=streak, total=total)


@router.get("/checkins", response_model=list[str])
async def list_checkin_dates(
    user_id: int | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """返回已打卡日期列表（YYYY-MM-DD），用于日历渲染。"""
    uid = user_id or user.id
    rows = (
        await db.execute(
            select(Checkin.checkin_date)
            .where(Checkin.user_id == uid)
            .order_by(Checkin.checkin_date)
        )
    ).scalars().all()
    return list(rows)


@router.get("/badges", response_model=list[BadgeOut])
async def list_badges(
    user_id: int | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    uid = user_id or user.id
    rows = (
        await db.execute(
            select(Badge).where(Badge.user_id == uid).order_by(Badge.created_at.desc())
        )
    ).scalars().all()
    return [
        BadgeOut(
            id=b.id,
            user_id=b.user_id,
            badge_type=b.badge_type,
            badge_name=b.badge_name,
            reason=b.reason,
            created_at=b.created_at,
        )
        for b in rows
    ]
