"""OpenAI 兼容适配器：覆盖 DeepSeek / 字节豆包 / 通义千问 / 智谱清言 / Ollama。

新增 OpenAI 兼容模型仅需给出 base_url 与默认模型名，无需编写新代码。
能力自动降级：不支持流式输出时调用方回退到 chat 同步聚合（见 factory/router）。
"""
from __future__ import annotations

import json
from typing import AsyncGenerator, Dict, List

import httpx

from app.services.ai.base import BaseAIGateway


class OpenAICompatibleAdapter(BaseAIGateway):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        default_model: str,
        proxy: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model or "gpt-3.5-turbo"
        self.proxy = proxy
        self.timeout = timeout

    # ------------------------------------------------------------------
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(proxy=self.proxy or None, timeout=self.timeout)

    # ------------------------------------------------------------------
    async def chat(
        self,
        messages: List[Dict],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        async with self._client() as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions", json=payload, headers=self._headers()
            )
            resp.raise_for_status()
            data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def stream_chat(
        self,
        messages: List[Dict],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        payload = {
            "model": self.default_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        async with self._client() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self._headers(),
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    chunk = line[len("data:") :].strip()
                    if chunk == "[DONE]":
                        break
                    try:
                        obj = json.loads(chunk)
                        delta = obj["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue

    async def check_connection(self) -> tuple[bool, str]:
        try:
            models = await self.list_models()
            if models:
                return True, f"连接成功，当前可用模型：{models[0]}"
            return True, "连接成功（未返回模型列表）"
        except Exception as e:  # noqa: BLE001
            return False, _friendly_error(e)

    async def list_models(self) -> List[str]:
        async with self._client() as client:
            resp = await client.get(f"{self.base_url}/models", headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
        return [m["id"] for m in data.get("data", [])]


def _friendly_error(e: Exception) -> str:
    msg = str(e)
    if "401" in msg or "Unauthorized" in msg:
        return "API Key 无效或已过期"
    if "404" in msg:
        return "地址错误或模型不存在"
    if "Connection" in msg or "ConnectError" in msg or "NameResolution" in msg:
        return "网络连接失败，请检查 Base URL 或代理设置"
    return msg[:200]
