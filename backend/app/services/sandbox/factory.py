"""沙箱工厂：根据配置切换实现（local / docker）。"""
from __future__ import annotations

from app.core.config import settings
from app.services.sandbox.base import SandboxBase
from app.services.sandbox.docker import DockerSandbox
from app.services.sandbox.local import LocalSandbox


def get_sandbox() -> SandboxBase:
    if settings.SANDBOX_BACKEND == "docker":
        return DockerSandbox()
    return LocalSandbox()
