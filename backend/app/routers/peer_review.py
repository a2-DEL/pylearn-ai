"""学生互评：针对作品墙作品提交评分与评语。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import PeerReview, Submission, User
from app.schemas.schemas import PeerReviewCreate, PeerReviewOut

router = APIRouter()


@router.post("/peer-reviews", response_model=PeerReviewOut)
async def create_review(
    req: PeerReviewCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    work = (
        await db.execute(select(Submission).where(Submission.id == req.work_id))
    ).scalars().first()
    if not work:
        raise HTTPException(status_code=404, detail="作品不存在")
    if work.user_id == user.id:
        raise HTTPException(status_code=400, detail="不能评价自己的作品")
    review = PeerReview(
        work_id=req.work_id,
        reviewer_id=user.id,
        score=req.score,
        comment=req.comment,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return PeerReviewOut(
        id=review.id,
        work_id=review.work_id,
        reviewer_id=review.reviewer_id,
        reviewer_name=user.username,
        score=review.score,
        comment=review.comment,
        created_at=review.created_at,
    )


@router.get("/peer-reviews", response_model=list[PeerReviewOut])
async def list_reviews(
    work_id: int = Query(...),
    db: AsyncSession = Depends(get_db),
):
    rows = (
        await db.execute(
            select(PeerReview)
            .where(PeerReview.work_id == work_id)
            .order_by(PeerReview.created_at.desc())
        )
    ).scalars().all()
    reviewer_ids = {r.reviewer_id for r in rows}
    name_map: dict[int, str] = {}
    if reviewer_ids:
        users = (
            await db.execute(select(User).where(User.id.in_(reviewer_ids)))
        ).scalars().all()
        name_map = {u.id: u.username for u in users}
    return [
        PeerReviewOut(
            id=r.id,
            work_id=r.work_id,
            reviewer_id=r.reviewer_id,
            reviewer_name=name_map.get(r.reviewer_id, f"user{r.reviewer_id}"),
            score=r.score,
            comment=r.comment,
            created_at=r.created_at,
        )
        for r in rows
    ]
