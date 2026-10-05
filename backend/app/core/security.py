"""安全工具：AES 加解密、API Key 脱敏、危险代码拦截。

- API Key 在数据库与本地存储中均为密文；接口只回显后 4 位。
- 危险代码黑名单用于本地沙箱兜底时的预检拦截（容器沙箱另有系统级隔离）。
"""
from __future__ import annotations

import base64
import hashlib
import re

from cryptography.fernet import Fernet
from jose import jwt

from app.core.config import settings

# ---------------------------------------------------------------------------
# AES / Fernet 加解密
# ---------------------------------------------------------------------------
def _fernet_key() -> bytes:
    raw = settings.AES_KEY
    if raw:
        return raw.encode("utf-8") if isinstance(raw, str) else raw
    # 开发态：基于 SECRET_KEY 派生 32 字节 URL-safe 密钥
    return base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest())


_fernet = Fernet(_fernet_key())


def encrypt_text(plain: str) -> str:
    """明文 -> 密文（base64 字符串）。"""
    if not plain:
        return ""
    return _fernet.encrypt(plain.encode("utf-8")).decode("utf-8")


def decrypt_text(cipher: str) -> str:
    """密文 -> 明文。"""
    if not cipher:
        return ""
    return _fernet.decrypt(cipher.encode("utf-8")).decode("utf-8")


def mask_api_key(key: str) -> str:
    """API Key 脱敏：仅保留最后 4 位，例如 sk-xxxxabcd -> ****abcd。"""
    if not key:
        return ""
    if len(key) <= 4:
        return "****"
    return f"****{key[-4:]}"


# ---------------------------------------------------------------------------
# 密码哈希（bcrypt）
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    import bcrypt

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    import bcrypt

    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 危险代码拦截（本地沙箱兜底预检）
# ---------------------------------------------------------------------------
_DANGEROUS_PATTERNS = [
    r"import\s+subprocess",
    r"from\s+subprocess\s+import",
    r"os\.system",
    r"os\.popen",
    r"os\.remove",
    r"os\.rmdir",
    r"os\.removedirs",
    r"os\.environ",
    r"os\.getenv",
    r"shutil\.(rmtree|remove)",
    r"import\s+socket",
    r"from\s+socket\s+import",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"__import__\s*\(\s*['\"](os|subprocess|socket|shutil)['\"]",
    r"open\s*\([^)]*,\s*['\"][^'\"]*['\"]\s*\)",  # 写文件（含模式参数的 open）
]

_COMPILED = [re.compile(p) for p in _DANGEROUS_PATTERNS]


def check_dangerous_code(code: str) -> str | None:
    """预检代码是否含危险模式。返回命中原因或 None。"""
    for pat in _COMPILED:
        m = pat.search(code)
        if m:
            return f"检测到受限操作（{m.group(0)}），出于安全考虑已拦截。如需文件/网络能力请使用容器沙箱。"
    return None


# ---------------------------------------------------------------------------
# JWT（用户认证令牌）
# ---------------------------------------------------------------------------
JWT_ALGORITHM = "HS256"


def create_access_token(sub: int, roles: str) -> str:
    """签发访问令牌，载荷含用户 ID 与角色串。"""
    payload = {"sub": str(sub), "roles": roles}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """解码并校验令牌，失败返回 None（不抛异常）。"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:  # noqa: BLE001
        return None
