"""知识点接口：三级知识架构查询。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import KnowledgePoint
from app.schemas.schemas import KnowledgePointOut

router = APIRouter()


@router.get("/knowledge", response_model=list[KnowledgePointOut])
async def list_knowledge(
    layer: str | None = Query(None, description="basic/tool/app"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(KnowledgePoint)
    if layer:
        stmt = stmt.where(KnowledgePoint.layer == layer)
    stmt = stmt.order_by(KnowledgePoint.order_index)
    rows = (await db.execute(stmt)).scalars().all()
    return [KnowledgePointOut.model_validate(r, from_attributes=True) for r in rows]


@router.get("/knowledge/{kp_id}", response_model=KnowledgePointOut)
async def get_knowledge(kp_id: int, db: AsyncSession = Depends(get_db)):
    kp = await db.get(KnowledgePoint, kp_id)
    if not kp:
        from app.core.exceptions import AppError

        raise AppError("知识点不存在", code=404)
    return KnowledgePointOut.model_validate(kp, from_attributes=True)
