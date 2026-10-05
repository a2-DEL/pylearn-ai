"""任务 / 作业管理：出题（题库/自定义/AI）、提交与自动批改、提交记录。

- 出题：从公共题库选择（复用 Task.class_id=null）、自定义、AI 生成
- 提交：校验截止时间/最大提交次数 -> 调用批改服务 -> 落库 Submission
- 权限：班级任务仅教师可创建/编辑；学生仅可提交与查看自己的提交
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_teacher
from app.core.exceptions import AppError
from app.models.models import Class, Submission, Task, User
from app.schemas.schemas import (
    GradingResult,
    SubmitRequest,
    TaskCreate,
    TaskOut,
)
from app.services.ai.factory import build_gateway_for_user
from app.services.ai.prompts import build_messages
from app.services.badges import maybe_award_full_score
from app.services.grading import _extract_json, grade_submission


def _to_task_out(t: Task) -> TaskOut:
    return TaskOut(
        id=t.id, class_id=t.class_id, creator_id=t.creator_id, title=t.title,
        description=t.description, knowledge_point=t.knowledge_point, difficulty=t.difficulty,
        test_cases=t.test_cases or [], hints=t.hints or [], deadline=t.deadline,
        max_submissions=t.max_submissions, allow_ai=t.allow_ai, source=t.source, created_at=t.created_at,
    )


router = APIRouter()


@router.post("/tasks", response_model=TaskOut)
async def create_task(req: TaskCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if req.class_id:
        cls = await db.get(Class, req.class_id)
        if not cls:
            raise AppError("班级不存在", code=404)
        if cls.teacher_id != user.id:
            raise AppError("仅班级教师可发布该班作业", code=403)
    task = Task(
        class_id=req.class_id, creator_id=user.id, title=req.title, description=req.description,
        knowledge_point=req.knowledge_point, difficulty=req.difficulty, test_cases=req.test_cases,
        hints=req.hints, deadline=req.deadline, max_submissions=req.max_submissions,
        allow_ai=req.allow_ai, source=req.source,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return _to_task_out(task)


@router.get("/tasks", response_model=list[TaskOut])
async def list_tasks(
    class_id: int | None = Query(None),
    bank: bool = Query(False),  # True=公共题库（class_id 为空）
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Task)
    if bank:
        stmt = stmt.where(Task.class_id.is_(None))
    elif class_id is not None:
        stmt = stmt.where(Task.class_id == class_id)
    stmt = stmt.order_by(Task.id.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return [_to_task_out(r) for r in rows]


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def get_task(task_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    t = await db.get(Task, task_id)
    if not t:
        raise AppError("任务不存在", code=404)
    return _to_task_out(t)


@router.put("/tasks/{task_id}", response_model=TaskOut)
async def update_task(task_id: int, req: TaskCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    t = await db.get(Task, task_id)
    if not t or t.creator_id != user.id:
        raise AppError("无权编辑该任务", code=403)
    data = req.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(t, k, v)
    await db.commit()
    await db.refresh(t)
    return _to_task_out(t)


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    t = await db.get(Task, task_id)
    if not t or t.creator_id != user.id:
        raise AppError("无权删除该任务", code=403)
    await db.delete(t)
    await db.commit()
    return {"code": 0, "message": "已删除"}


@router.post("/tasks/generate")
async def generate_tasks(
    major: str = Query(""), knowledge: str = Query(""), difficulty: str = "easy",
    count: int = Query(3, ge=1, le=10),
    class_id: int | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """AI 生成题目：输入知识点/难度/数量，调用模型生成并保存为任务。"""
    gw = await build_gateway_for_user(user.id, db)
    messages = build_messages("problem_generate", knowledge=knowledge or major or "Python基础", difficulty=difficulty, count=count)
    content = await gw.chat(messages, temperature=0.7, max_tokens=2048)
    items = _extract_json(content)
    if not isinstance(items, list) or not items:
        raise AppError("AI 未能生成有效题目，请重试或调整描述", code=502)
    created = []
    for it in items[:count]:
        task = Task(
            class_id=class_id, creator_id=user.id, title=str(it.get("title", "AI 生成题")),
            description=str(it.get("description", "")), knowledge_point=str(it.get("knowledge_point", "")),
            difficulty=str(it.get("difficulty", difficulty)),
            test_cases=it.get("test_cases", []) or [], hints=it.get("hints", []) or [],
            source="ai",
        )
        db.add(task)
        created.append(task)
    await db.commit()
    return {"code": 0, "message": f"已生成 {len(created)} 题", "data": [_to_task_out(t) for t in created]}


@router.post("/tasks/{task_id}/submit", response_model=GradingResult)
async def submit_task(task_id: int, req: SubmitRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise AppError("任务不存在", code=404)

    # 截止时间校验
    if task.deadline and datetime.utcnow() > task.deadline:
        raise AppError("任务已截止，无法提交", code=400)

    # 最大提交次数校验
    sub_count = (
        await db.execute(
            select(func.count())
            .select_from(Submission)
            .where(Submission.task_id == task_id, Submission.user_id == user.id)
        )
    ).scalar() or 0
    if sub_count >= task.max_submissions:
        raise AppError(f"已达最大提交次数（{task.max_submissions}）", code=400)

    if not task.allow_ai and req.mode != "track_a":
        raise AppError("该任务不允许使用 AI 辅助", code=400)

    teacher_id = None
    if task.class_id:
        cls = await db.get(Class, task.class_id)
        teacher_id = cls.teacher_id if cls else None

    result = await grade_submission(
        db, code=req.code, task=task, student_id=user.id, teacher_id=teacher_id
    )

    sub = Submission(
        task_id=task.id, problem_id=None, user_id=user.id, code=req.code, mode=req.mode,
        status=result["status"], score=result["score"], run_time=result["run_time"],
        error_msg=result["error_msg"], ai_comment=result["ai_comment"], passed=result["passed"],
        similar_flag=result["similar_flag"],
    )
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    # 批改成功后触发徽章发放（满分作业）
    if sub.passed and sub.score >= 100:
        await maybe_award_full_score(user.id, sub.score, db)
    result["submission_id"] = sub.id
    return result


@router.get("/tasks/{task_id}/submissions")
async def task_submissions(task_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    task = await db.get(Task, task_id)
    if not task:
        raise AppError("任务不存在", code=404)
    is_teacher = task.class_id and (
        (await db.get(Class, task.class_id)).teacher_id == user.id
    ) if task.class_id else (task.creator_id == user.id)
    stmt = select(Submission).where(Submission.task_id == task_id)
    if not is_teacher:
        stmt = stmt.where(Submission.user_id == user.id)
    stmt = stmt.order_by(Submission.submitted_at.desc())
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": s.id, "user_id": s.user_id, "mode": s.mode, "status": s.status,
            "score": s.score, "run_time": s.run_time, "passed": s.passed,
            "error_msg": s.error_msg, "ai_comment": s.ai_comment, "similar_flag": s.similar_flag,
            "submitted_at": s.submitted_at,
        }
        for s in rows
    ]
