"""题目接口：编程训练场题目列表与详情。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import Problem
from app.schemas.schemas import ProblemOut

router = APIRouter()


@router.get("/problems", response_model=list[ProblemOut])
async def list_problems(
    difficulty: str | None = Query(None),
    knowledge_point: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Problem)
    if difficulty:
        stmt = stmt.where(Problem.difficulty == difficulty)
    if knowledge_point:
        stmt = stmt.where(Problem.knowledge_point == knowledge_point)
    rows = (await db.execute(stmt)).scalars().all()
    return [ProblemOut.model_validate(r, from_attributes=True) for r in rows]


@router.get("/problems/{problem_id}", response_model=ProblemOut)
async def get_problem(problem_id: int, db: AsyncSession = Depends(get_db)):
    p = await db.get(Problem, problem_id)
    if not p:
        from app.core.exceptions import AppError

        raise AppError("题目不存在", code=404)
    return ProblemOut.model_validate(p, from_attributes=True)
