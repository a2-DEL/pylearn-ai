"""代码沙箱抽象基类。业务层只依赖此接口，新增沙箱实现无需改动业务代码。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class SandboxBase(ABC):
    @abstractmethod
    async def run(
        self, code: str, timeout: int = 10, enable_network: bool = False
    ) -> Dict[str, Any]:
        """执行 Python 代码。

        返回结构：
        {
            "stdout": str,    # 标准输出
            "stderr": str,    # 标准错误
            "run_time": float,  # 运行时长（秒）
            "success": bool,    # 是否成功（返回码 0）
            "error": str,       # 友好错误信息（失败时）
        }
        """
