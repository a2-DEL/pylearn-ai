"""班级数据看板：概览卡片、知识点掌握热力图、学困生预警、成绩导出。

- 概览：总人数、任务完成率、平均分、总提交次数
- 热力图：各知识点（按任务 knowledge_point）平均得分/通过率
- 预警：连续未提交或错误率过高的学生
- 导出：成绩表 CSV（学生 × 任务）
"""
from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import AppError
from app.models.models import Class, ClassMember, Submission, Task, User


router = APIRouter()


@router.get("/stats/class/{class_id}")
async def class_stats(class_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cls = await db.get(Class, class_id)
    if not cls:
        raise AppError("班级不存在", code=404)
    if cls.teacher_id != user.id:
        member = (
            await db.execute(select(ClassMember).where(ClassMember.class_id == class_id, ClassMember.user_id == user.id))
        ).scalars().first()
        if not member:
            raise AppError("无权查看该班级数据", code=403)

    members = (
        await db.execute(select(ClassMember).where(ClassMember.class_id == class_id))
    ).scalars().all()
    member_ids = [m.user_id for m in members]
    tasks = (
        await db.execute(select(Task).where(Task.class_id == class_id))
    ).scalars().all()
    task_ids = [t.id for t in tasks]

    submissions = []
    if task_ids:
        submissions = (
            await db.execute(select(Submission).where(Submission.task_id.in_(task_ids)))
        ).scalars().all()

    total_students = len(member_ids)
    total_submissions = len(submissions)
    avg_score = round(sum(s.score for s in submissions) / total_submissions, 1) if total_submissions else 0.0
    track_a = sum(1 for s in submissions if s.mode == "track_a")
    track_b = sum(1 for s in submissions if s.mode == "track_b")

    submitted_users = {s.user_id for s in submissions}
    completion_rate = round(len(submitted_users & set(member_ids)) / total_students * 100, 1) if total_students else 0.0

    # 知识点热力图：按 task.knowledge_point 聚合平均分
    task_kp = {t.id: t.knowledge_point for t in tasks}
    heat: dict[str, list[int]] = {}
    for s in submissions:
        kp = task_kp.get(s.task_id, "未分类")
        heat.setdefault(kp, []).append(s.score)
    heatmap = [
        {"knowledge_point": kp, "avg_score": round(sum(v) / len(v), 1), "count": len(v)}
        for kp, v in heat.items()
    ]

    # 学困生预警：未提交 或 平均未通过
    warn = []
    for m in members:
        own = [s for s in submissions if s.user_id == m.user_id]
        if not own:
            warn.append({"user_id": m.user_id, "reason": "尚未提交任何作业"})
            continue
        passed_rate = sum(1 for s in own if s.passed) / len(own)
        if passed_rate < 0.5:
            warn.append({"user_id": m.user_id, "reason": f"通过率偏低（{round(passed_rate*100)}%）"})

    return {
        "code": 0,
        "data": {
            "overview": {
                "total_students": total_students,
                "total_tasks": len(tasks),
                "total_submissions": total_submissions,
                "completion_rate": completion_rate,
                "avg_score": avg_score,
                "track_a": track_a,
                "track_b": track_b,
            },
            "heatmap": heatmap,
            "warnings": warn,
        },
    }


@router.get("/stats/class/{class_id}/export")
async def export_csv(class_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """导出成绩表 CSV（学生 × 任务）。"""
    cls = await db.get(Class, class_id)
    if not cls or cls.teacher_id != user.id:
        raise AppError("仅班级教师可导出成绩", code=403)

    members = (
        await db.execute(
            select(ClassMember.user_id, User.username)
            .join(User, User.id == ClassMember.user_id)
            .where(ClassMember.class_id == class_id)
        )
    ).all()
    tasks = (
        await db.execute(select(Task).where(Task.class_id == class_id).order_by(Task.id))
    ).scalars().all()
    subs = (
        await db.execute(select(Submission).where(Submission.task_id.in_([t.id for t in tasks])))
    ).scalars().all() if tasks else []

    score_map: dict[tuple[int, int], int] = {(s.user_id, s.task_id): s.score for s in subs}

    buf = io.StringIO()
    writer = csv.writer(buf)
    header = ["用户名"] + [t.title for t in tasks] + ["平均分"]
    writer.writerow(header)
    for uid, uname in members:
        row = [uname]
        scores = []
        for t in tasks:
            sc = score_map.get((uid, t.id))
            row.append(sc if sc is not None else "")
            if sc is not None:
                scores.append(sc)
        row.append(round(sum(scores) / len(scores), 1) if scores else 0)
        writer.writerow(row)

    return {
        "code": 0,
        "data": {"filename": f"class_{class_id}_grades.csv", "csv": buf.getvalue()},
    }
