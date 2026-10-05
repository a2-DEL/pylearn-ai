"""学习进度接口：按知识点记录状态与正确率（教师/学生个人中心联动）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import AppError
from app.models.models import LearningProgress, User
from app.schemas.schemas import ProgressOut, ProgressUpsert


def _to_out(p: LearningProgress) -> ProgressOut:
    return ProgressOut(
        id=p.id, user_id=p.user_id, knowledge_point=p.knowledge_point,
        status=p.status, accuracy=p.accuracy, updated_at=p.updated_at,
    )


router = APIRouter()


@router.put("/learning-progress", response_model=ProgressOut)
async def upsert_progress(req: ProgressUpsert, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    row = (
        await db.execute(
            select(LearningProgress).where(
                LearningProgress.user_id == user.id,
                LearningProgress.knowledge_point == req.knowledge_point,
            )
        )
    ).scalars().first()
    if row:
        row.status = req.status
        row.accuracy = req.accuracy
    else:
        row = LearningProgress(
            user_id=user.id, knowledge_point=req.knowledge_point,
            status=req.status, accuracy=req.accuracy,
        )
        db.add(row)
    await db.commit()
    await db.refresh(row)
    return _to_out(row)


@router.get("/learning-progress", response_model=list[ProgressOut])
async def my_progress(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(select(LearningProgress).where(LearningProgress.user_id == user.id))
    ).scalars().all()
    return [_to_out(r) for r in rows]


@router.get("/learning-progress/{knowledge_point}", response_model=ProgressOut)
async def one_progress(knowledge_point: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    row = (
        await db.execute(
            select(LearningProgress).where(
                LearningProgress.user_id == user.id,
                LearningProgress.knowledge_point == knowledge_point,
            )
        )
    ).scalars().first()
    if not row:
        raise AppError("暂无该知识点进度", code=404)
    return _to_out(row)
