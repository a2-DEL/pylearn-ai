"""班级 / 全校排行榜：基于 Submission 聚合。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import ClassMember, Submission, User
from app.schemas.schemas import RankEntry, RankOut

router = APIRouter()


@router.get("/rank", response_model=RankOut)
async def get_rank(
    scope: str = Query("class", description="class/school"),
    class_id: int | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """聚合提交成绩生成排行。班级范围仅统计班级成员。"""
    user_ids: list[int] | None = None
    if scope == "class":
        if not class_id:
            return RankOut(scope=scope, class_id=class_id, entries=[])
        members = (
            await db.execute(
                select(ClassMember.user_id).where(ClassMember.class_id == class_id)
            )
        ).scalars().all()
        user_ids = list(members)
        if not user_ids:
            return RankOut(scope=scope, class_id=class_id, entries=[])

    stmt = (
        select(
            Submission.user_id,
            func.coalesce(func.sum(Submission.score), 0).label("total_score"),
            func.count().label("submission_count"),
            func.count().filter(Submission.passed == True).label("passed_count"),  # noqa: E712
        )
        .group_by(Submission.user_id)
    )
    if user_ids is not None:
        stmt = stmt.where(Submission.user_id.in_(user_ids))

    rows = (await db.execute(stmt)).all()
    id_to_score = {r.user_id: int(r.total_score) for r in rows}
    id_to_count = {r.user_id: int(r.submission_count) for r in rows}
    id_to_passed = {r.user_id: int(r.passed_count) for r in rows}

    user_ids_all = list(id_to_score.keys())
    entries: list[RankEntry] = []
    if user_ids_all:
        users = (
            await db.execute(select(User).where(User.id.in_(user_ids_all)))
        ).scalars().all()
        name_map = {u.id: u.username for u in users}
        for uid in user_ids_all:
            cnt = id_to_count[uid] or 1
            entries.append(
                RankEntry(
                    user_id=uid,
                    username=name_map.get(uid, f"user{uid}"),
                    total_score=id_to_score[uid],
                    passed_count=id_to_passed.get(uid, 0),
                    submission_count=id_to_count[uid],
                    avg_score=round(id_to_score[uid] / cnt, 1),
                )
            )
    entries.sort(key=lambda e: e.total_score, reverse=True)
    return RankOut(scope=scope, class_id=class_id, entries=entries)
