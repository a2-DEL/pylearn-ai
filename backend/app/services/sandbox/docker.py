"""Docker 容器沙箱：单次运行单次销毁（占位）。

当前环境未安装 Docker SDK，保留接口与镜像规范：
- 基础镜像 python:3.11-slim，预装全量库；
- 资源限制：内存 256M、CPU 0.5 核、超时 10s；
- 网络默认隔离，爬虫题 enable_network=True 放开；
- 文件隔离：仅标准输入输出，不挂载宿主机目录。

接入时安装 docker 依赖并补充 _run_in_container 即可平滑切换（SANDBOX_BACKEND=docker）。
"""
from __future__ import annotations

from typing import Any, Dict

from app.services.sandbox.base import SandboxBase


class DockerSandbox(SandboxBase):
    async def run(
        self, code: str, timeout: int = 10, enable_network: bool = False
    ) -> Dict[str, Any]:
        raise NotImplementedError(
            "Docker 沙箱尚未启用：请先安装 `docker` 依赖并在宿主机启动 Docker，"
            "随后设置环境变量 SANDBOX_BACKEND=docker。当前可临时使用本地兜底沙箱。"
        )
