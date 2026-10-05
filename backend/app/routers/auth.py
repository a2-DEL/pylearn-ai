"""用户认证与权限接口：注册、登录(JWT)、当前用户、修改密码。

- 注册：用户名唯一；密码 bcrypt 哈希；roles 支持 student/teacher 组合
- 登录：校验密码后签发 JWT；同一账号可含多角色（身份切换由前端处理）
"""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import AppError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.models import User
from app.schemas.schemas import (
    LoginRequest,
    PasswordUpdate,
    RegisterRequest,
    TokenOut,
    UserOut,
)


def _to_user_out(u: User) -> UserOut:
    return UserOut(
        id=u.id,
        username=u.username,
        email=u.email,
        roles=u.roles,
        created_at=u.created_at,
        last_login=u.last_login,
    )


router = APIRouter()


@router.post("/auth/register", response_model=TokenOut)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    dup = (
        await db.execute(select(User).where(User.username == req.username))
    ).scalars().first()
    if dup:
        raise AppError("用户名已存在", code=409)
    if req.email:
        email_dup = (
            await db.execute(select(User).where(User.email == req.email))
        ).scalars().first()
        if email_dup:
            raise AppError("邮箱已被注册", code=409)
    user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        roles=req.roles,
        last_login=datetime.utcnow(),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    token = create_access_token(user.id, user.roles)
    return TokenOut(access_token=token, user_id=user.id, username=user.username, roles=user.roles)


@router.post("/auth/login", response_model=TokenOut)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = (
        await db.execute(select(User).where(User.username == req.username))
    ).scalars().first()
    if not user or not verify_password(req.password, user.password_hash):
        raise AppError("用户名或密码错误", code=401)
    user.last_login = datetime.utcnow()
    await db.commit()
    token = create_access_token(user.id, user.roles)
    return TokenOut(access_token=token, user_id=user.id, username=user.username, roles=user.roles)


@router.get("/auth/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return _to_user_out(user)


@router.put("/auth/password")
async def change_password(req: PasswordUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not verify_password(req.old_password, user.password_hash):
        raise AppError("原密码错误", code=400)
    user.password_hash = hash_password(req.new_password)
    await db.commit()
    return {"code": 0, "message": "密码已更新"}
