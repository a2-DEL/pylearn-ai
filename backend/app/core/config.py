"""全局配置：使用 Pydantic Settings，支持环境变量覆盖，避免硬编码。"""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（backend/ 的上一级）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # 应用
    APP_NAME: str = "PyLearn AI"
    DEBUG: bool = False

    # 数据库：默认 SQLite，可通过 DATABASE_URL 切换到 PostgreSQL
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(BASE_DIR, 'pylearn.db')}"

    # 安全：生产环境务必通过环境变量覆盖 SECRET_KEY / AES_KEY
    SECRET_KEY: str = "dev-secret-change-me"
    AES_KEY: str = ""  # 留空则基于 SECRET_KEY 派生 Fernet 密钥

    # CORS：生产环境改为前端域名
    CORS_ORIGINS: str = "*"

    # 沙箱：local(本地兜底) / docker(容器)
    SANDBOX_BACKEND: str = "local"
    SANDBOX_TIMEOUT: int = 10
    SANDBOX_MAX_OUTPUT: int = 10000

    # AI 限流（个人用户）
    AI_RATE_PER_MIN: int = 20
    AI_RATE_PER_DAY: int = 200

    # 集中式限流：配置 REDIS_URL 后启用 Redis 滑动窗口限流（多副本安全），
    # 留空则回退进程内内存限流（单副本 / 本地开发）。
    REDIS_URL: str = ""

    # 前端 AES 加密盐（与前端保持一致即可）
    FRONTEND_AES_SALT: str = "pylearn-ai-salt"

    @property
    def cors_origin_list(self) -> list[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
