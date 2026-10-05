"""作品墙：展示通过的公开提交，支持点赞。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import Problem, Submission, User
from app.schemas.schemas import WorkLikeResponse, WorkOut

router = APIRouter()


@router.get("/works", response_model=list[WorkOut])
async def list_works(
    class_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """公开且通过的提交作品。"""
    stmt = (
        select(Submission)
        .where(Submission.passed == True)  # noqa: E712
        .where(Submission.is_public == True)  # noqa: E712
        .order_by(Submission.submitted_at.desc())
        .limit(limit)
    )
    rows = (await db.execute(stmt)).scalars().all()

    prob_ids = {s.problem_id for s in rows if s.problem_id}
    title_map: dict[int, str] = {}
    if prob_ids:
        probs = (
            await db.execute(select(Problem).where(Problem.id.in_(prob_ids)))
        ).scalars().all()
        title_map = {p.id: p.title for p in probs}

    user_ids = {s.user_id for s in rows}
    name_map: dict[int, str] = {}
    if user_ids:
        users = (
            await db.execute(select(User).where(User.id.in_(user_ids)))
        ).scalars().all()
        name_map = {u.id: u.username for u in users}

    return [
        WorkOut(
            id=s.id,
            user_id=s.user_id,
            username=name_map.get(s.user_id, f"user{s.user_id}"),
            problem_id=s.problem_id,
            problem_title=title_map.get(s.problem_id, "") if s.problem_id else "",
            task_id=s.task_id,
            code=s.code,
            score=s.score,
            run_time=s.run_time,
            submitted_at=s.submitted_at,
            likes=s.likes,
        )
        for s in rows
    ]


@router.post("/works/{work_id}/like", response_model=WorkLikeResponse)
async def like_work(
    work_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = (
        await db.execute(select(Submission).where(Submission.id == work_id))
    ).scalars().first()
    if not sub:
        raise HTTPException(status_code=404, detail="作品不存在")
    sub.likes = (sub.likes or 0) + 1
    await db.commit()
    return WorkLikeResponse(likes=sub.likes)
