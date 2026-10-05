"""Mock 适配器：无需 API Key 即可演示全部 AI 流程（降级可用）。"""
from __future__ import annotations

import asyncio
from typing import AsyncGenerator, Dict, List

from app.services.ai.base import BaseAIGateway


class MockAdapter(BaseAIGateway):
    def __init__(self, default_model: str = "mock-python-tutor") -> None:
        self.default_model = default_model

    def _build(self, prompt: str) -> str:
        snippet = prompt[:200].replace("\n", " ")
        return (
            "【Mock 模式演示】你当前未配置真实 API Key，以下是模拟回复：\n\n"
            f"你的问题：{snippet}\n\n"
            "建议学习路径：\n"
            "1) 先理解题意与输入输出格式；\n"
            "2) 将问题拆解为可执行的步骤；\n"
            "3) 编写代码并在右侧运行验证；\n"
            "4) 根据报错定位问题（注意看错误行号）。\n\n"
            "在「AI 设置」中配置 DeepSeek / 通义千问等厂商的 Key 后，即可获得真实 AI 辅导与代码评审。"
        )

    async def chat(
        self, messages: List[Dict], temperature: float = 0.3, max_tokens: int = 1024
    ) -> str:
        last = messages[-1]["content"] if messages else ""
        return self._build(last)

    async def stream_chat(
        self, messages: List[Dict], temperature: float = 0.3, max_tokens: int = 1024
    ) -> AsyncGenerator[str, None]:
        text = self._build(messages[-1]["content"] if messages else "")
        for token in text.replace("\n", "\n\n").split(" "):
            yield token + " "
            await asyncio.sleep(0.015)

    async def check_connection(self) -> tuple[bool, str]:
        return True, "连接成功（Mock 模式，无需 Key）"

    async def list_models(self) -> List[str]:
        return ["mock-python-tutor"]
