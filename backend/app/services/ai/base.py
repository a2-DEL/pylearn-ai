"""统一 AI 网关抽象基类（规范 5.2）。

所有模型适配器必须实现 chat / stream_chat / check_connection / list_models，
业务层只依赖此接口，完全不感知底层模型差异。
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, List


class BaseAIGateway(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """普通同步对话，返回完整文本。"""
        raise NotImplementedError

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[Dict],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """流式对话，逐块返回文本。"""
        raise NotImplementedError
        yield  # pragma: no cover

    @abstractmethod
    async def check_connection(self) -> tuple[bool, str]:
        """测试连接，返回 (是否成功, 错误信息/模型名称)。"""
        raise NotImplementedError

    @abstractmethod
    async def list_models(self) -> List[str]:
        """获取可用模型列表。"""
        raise NotImplementedError
