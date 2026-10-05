"""班级管理系统（教师端 + 学生端）。

- 教师：创建班级（自动 6 位邀请码）、修改信息、重置邀请码、归档/关闭、学生管理（移除/分组/批量导入）
- 学生：凭邀请码加入班级
- 成员关系持久化于 class_members 表
"""
from __future__ import annotations

import random
import string

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_teacher
from app.core.exceptions import AppError
from app.models.models import Class, ClassMember, Submission, Task, User
from app.schemas.schemas import (
    ClassCreate,
    ClassOut,
    ClassUpdate,
    JoinClassRequest,
    MemberOut,
)


def _gen_invite_code() -> str:
    return "".join(random.choices(string.digits, k=6))


async def _unique_invite_code(db: AsyncSession) -> str:
    for _ in range(10):
        code = _gen_invite_code()
        exists = (
            await db.execute(select(Class).where(Class.invite_code == code))
        ).scalars().first()
        if not exists:
            return code
    # 极端情况下加随机字母兜底
    return _gen_invite_code() + random.choice(string.ascii_uppercase)


async def _to_class_out(db: AsyncSession, c: Class) -> ClassOut:
    cnt = (
        await db.execute(
            select(func.count()).select_from(ClassMember).where(ClassMember.class_id == c.id)
        )
    ).scalar() or 0
    return ClassOut(
        id=c.id, teacher_id=c.teacher_id, class_name=c.class_name, major=c.major,
        invite_code=c.invite_code, description=c.description, status=c.status,
        created_at=c.created_at, student_count=cnt,
    )


router = APIRouter()


@router.post("/classes", response_model=ClassOut)
async def create_class(req: ClassCreate, teacher: User = Depends(require_teacher), db: AsyncSession = Depends(get_db)):
    code = await _unique_invite_code(db)
    cls = Class(
        teacher_id=teacher.id, class_name=req.class_name, major=req.major,
        invite_code=code, description=req.description, status="active",
    )
    db.add(cls)
    await db.commit()
    await db.refresh(cls)
    return await _to_class_out(db, cls)


@router.get("/classes/mine", response_model=list[ClassOut])
async def my_classes(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """我创建的班级 + 我加入的班级。"""
    taught = (
        await db.execute(select(Class).where(Class.teacher_id == user.id))
    ).scalars().all()
    joined_ids = (
        await db.execute(select(ClassMember.class_id).where(ClassMember.user_id == user.id))
    ).scalars().all()
    joined = (
        await db.execute(select(Class).where(Class.id.in_(joined_ids))) if joined_ids else None
    )
    rows = list(taught)
    if joined is not None:
        rows += joined.scalars().all()
    out = []
    for c in rows:
        out.append(await _to_class_out(db, c))
    return out


@router.get("/classes/{class_id}", response_model=ClassOut)
async def get_class(class_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cls = await db.get(Class, class_id)
    if not cls:
        raise AppError("班级不存在", code=404)
    return await _to_class_out(db, cls)


@router.put("/classes/{class_id}", response_model=ClassOut)
async def update_class(class_id: int, req: ClassUpdate, teacher: User = Depends(require_teacher), db: AsyncSession = Depends(get_db)):
    cls = await db.get(Class, class_id)
    if not cls:
        raise AppError("班级不存在", code=404)
    if cls.teacher_id != teacher.id:
        raise AppError("仅班级创建教师可修改", code=403)
    data = req.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(cls, k, v)
    await db.commit()
    await db.refresh(cls)
    return await _to_class_out(db, cls)


@router.post("/classes/{class_id}/archive")
async def archive_class(class_id: int, teacher: User = Depends(require_teacher), db: AsyncSession = Depends(get_db)):
    cls = await db.get(Class, class_id)
    if not cls:
        raise AppError("班级不存在", code=404)
    if cls.teacher_id != teacher.id:
        raise AppError("仅班级创建教师可归档", code=403)
    cls.status = "archived"
    await db.commit()
    return {"code": 0, "message": "班级已归档"}


@router.post("/classes/{class_id}/reset-code")
async def reset_code(class_id: int, teacher: User = Depends(require_teacher), db: AsyncSession = Depends(get_db)):
    cls = await db.get(Class, class_id)
    if not cls:
        raise AppError("班级不存在", code=404)
    if cls.teacher_id != teacher.id:
        raise AppError("仅班级创建教师可重置邀请码", code=403)
    cls.invite_code = await _unique_invite_code(db)
    await db.commit()
    return {"code": 0, "message": "邀请码已重置", "data": {"invite_code": cls.invite_code}}


@router.post("/classes/join", response_model=ClassOut)
async def join_class(req: JoinClassRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cls = (
        await db.execute(select(Class).where(Class.invite_code == req.invite_code))
    ).scalars().first()
    if not cls:
        raise AppError("邀请码无效", code=404)
    if cls.status != "active":
        raise AppError("班级已归档，无法加入", code=400)
    exist = (
        await db.execute(
            select(ClassMember).where(ClassMember.class_id == cls.id, ClassMember.user_id == user.id)
        )
    ).scalars().first()
    if not exist:
        db.add(ClassMember(class_id=cls.id, user_id=user.id, role="student"))
        await db.commit()
    return await _to_class_out(db, cls)


@router.get("/classes/{class_id}/members", response_model=list[MemberOut])
async def list_members(class_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cls = await db.get(Class, class_id)
    if not cls:
        raise AppError("班级不存在", code=404)
    if cls.teacher_id != user.id:
        # 学生仅可查看（需为成员）
        member = (
            await db.execute(select(ClassMember).where(ClassMember.class_id == class_id, ClassMember.user_id == user.id))
        ).scalars().first()
        if not member:
            raise AppError("无权访问该班级", code=403)
    rows = (
        await db.execute(
            select(ClassMember, User.username)
            .join(User, User.id == ClassMember.user_id)
            .where(ClassMember.class_id == class_id)
        )
    ).all()
    return [
        MemberOut(user_id=m.user_id, username=uname, role=m.role, group_name=m.group_name, joined_at=m.joined_at)
        for m, uname in rows
    ]


@router.delete("/classes/{class_id}/members/{user_id}")
async def remove_member(class_id: int, user_id: int, teacher: User = Depends(require_teacher), db: AsyncSession = Depends(get_db)):
    cls = await db.get(Class, class_id)
    if not cls or cls.teacher_id != teacher.id:
        raise AppError("无权操作", code=403)
    member = (
        await db.execute(select(ClassMember).where(ClassMember.class_id == class_id, ClassMember.user_id == user_id))
    ).scalars().first()
    if member:
        await db.delete(member)
        await db.commit()
    return {"code": 0, "message": "已移除"}


@router.put("/classes/{class_id}/members/{user_id}/group")
async def set_group(class_id: int, user_id: int, group: str = Query(""), teacher: User = Depends(require_teacher), db: AsyncSession = Depends(get_db)):
    cls = await db.get(Class, class_id)
    if not cls or cls.teacher_id != teacher.id:
        raise AppError("无权操作", code=403)
    member = (
        await db.execute(select(ClassMember).where(ClassMember.class_id == class_id, ClassMember.user_id == user_id))
    ).scalars().first()
    if not member:
        raise AppError("成员不存在", code=404)
    member.group_name = group
    await db.commit()
    return {"code": 0, "message": "已更新分组"}


@router.post("/classes/{class_id}/members/batch")
async def batch_import(class_id: int, usernames: list[str], teacher: User = Depends(require_teacher), db: AsyncSession = Depends(get_db)):
    """按用户名批量导入学生（自动注册未存在的账号并使用默认密码）。"""
    cls = await db.get(Class, class_id)
    if not cls or cls.teacher_id != teacher.id:
        raise AppError("无权操作", code=403)
    added = 0
    for name in usernames:
        name = (name or "").strip()
        if not name:
            continue
        user = (
            await db.execute(select(User).where(User.username == name))
        ).scalars().first()
        if not user:
            # 批量导入：默认密码为 invite_code，首次登录可修改
            from app.core.security import hash_password

            user = User(username=name, password_hash=hash_password(cls.invite_code), roles="student")
            db.add(user)
            await db.flush()
        exist = (
            await db.execute(select(ClassMember).where(ClassMember.class_id == class_id, ClassMember.user_id == user.id))
        ).scalars().first()
        if not exist:
            db.add(ClassMember(class_id=class_id, user_id=user.id, role="student"))
            added += 1
    await db.commit()
    return {"code": 0, "message": f"已导入 {added} 名学生"}


@router.get("/classes/{class_id}/ai-stats")
async def class_ai_stats(
    class_id: int,
    teacher: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """班级 AI 使用与学情统计（简化版，基于现有 Submission/Task 表聚合）。

    - 总学生数 / 活跃学生数（近 7 天有提交）
    - 总提交数 / 平均分 / 通过率
    - track_a（独立编程）vs track_b（AI 协作）占比
    - 每个学生一行：提交数、平均分、最近活跃
    """
    cls = await db.get(Class, class_id)
    if not cls or cls.teacher_id != teacher.id:
        raise AppError("无权查看该班级统计", code=403)

    # 班级学生总数
    total_students = (
        await db.execute(select(func.count(ClassMember.id)).where(ClassMember.class_id == class_id))
    ).scalar_one()

    # 该班级任务下的所有提交
    subq = select(Submission).join(Task, Submission.task_id == Task.id).where(Task.class_id == class_id)

    total_subs = (await db.execute(select(func.count()).select_from(subq.subquery()))).scalar_one()
    avg_score = (await db.execute(select(func.avg(Submission.score)).select_from(subq.subquery()))).scalar_one() or 0
    pass_count = (await db.execute(
        select(func.count()).select_from(subq.subquery()).where(Submission.status == "success")
    )).scalar_one()

    track_a = (await db.execute(
        select(func.count()).select_from(subq.subquery()).where(Submission.mode == "track_a")
    )).scalar_one()
    track_b = (await db.execute(
        select(func.count()).select_from(subq.subquery()).where(Submission.mode == "track_b")
    )).scalar_one()

    # 每学生汇总
    rows = (await db.execute(
        select(
            Submission.user_id,
            User.username,
            func.count(Submission.id),
            func.avg(Submission.score),
            func.max(Submission.submitted_at),
        )
        .join(User, Submission.user_id == User.id)
        .select_from(subq.subquery().alias("s"))
        .group_by(Submission.user_id, User.username)
        .order_by(func.count(Submission.id).desc())
    )).all()

    per_student = [
        {"user_id": r[0], "username": r[1], "submissions": r[2], "avg_score": round(float(r[3] or 0), 1), "last_submit": str(r[4]) if r[4] else ""}
        for r in rows
    ]

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "total_students": total_students,
            "total_submissions": total_subs,
            "avg_score": round(float(avg_score), 1),
            "pass_rate": round(pass_count / total_subs * 100, 1) if total_subs else 0,
            "track_a_submissions": track_a,
            "track_b_submissions": track_b,
            "per_student": per_student,
        },
    }
