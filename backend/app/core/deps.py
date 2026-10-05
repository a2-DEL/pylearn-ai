"""依赖注入：当前登录用户与教师权限校验。

- get_current_user: 解析 Bearer 令牌，返回 User ORM 对象；失败抛 401
- require_teacher: 在 get_current_user 基础上校验 roles 含 teacher，否则 403
- get_optional_user: 游客模式（未登录返回 None），用于降级可用场景
"""
from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.core.exceptions import AppError
from app.core.security import decode_access_token
from app.models.models import User


_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db=Depends(get_db),
) -> User:
    if not cred or not cred.credentials:
        raise AppError("未登录或登录已过期", code=401)
    payload = decode_access_token(cred.credentials)
    if payload is None:
        raise AppError("登录凭证无效，请重新登录", code=401)
    user = await db.get(User, int(payload.get("sub", 0) or 0))
    if not user:
        raise AppError("用户不存在", code=401)
    return user


async def get_optional_user(
    cred: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db=Depends(get_db),
) -> User | None:
    """游客降级：未登录返回 None。"""
    if not cred or not cred.credentials:
        return None
    payload = decode_access_token(cred.credentials)
    if payload is None:
        return None
    return await db.get(User, int(payload.get("sub", 0) or 0))


async def require_teacher(user: User = Depends(get_current_user)) -> User:
    if "teacher" not in user.roles.split(","):
        raise AppError("需要教师权限", code=403)
    return user
