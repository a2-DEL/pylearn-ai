"""AI 对话 / 答疑 / 自动识别接口。游客模式：Key 由前端传入，服务端不落库。"""
from __future__ import annotations

import json
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.schemas import ChatRequest, ExplainRequest
from app.services.ai.detector import auto_detect
from app.services.ai.factory import build_gateway
from app.services.ai.prompts import build_messages
from app.services.ai.ratelimit import check_ai_rate
from app.services.ai.stream import sse_data, sse_done

router = APIRouter()


def _gw(req: ChatRequest):
    return build_gateway(req.provider, req.api_key, req.base_url, req.model)


@router.post("/ai/chat")
async def chat(req: ChatRequest, request: Request, db: AsyncSession = Depends(get_db)):
    await check_ai_rate(request)
    gw = _gw(req)
    try:
        content = await gw.chat(req.messages, req.temperature, req.max_tokens)
    except Exception:  # 自动重试 1 次（降级机制）
        content = await gw.chat(req.messages, req.temperature, req.max_tokens)
    return {"code": 0, "message": "ok", "data": {"content": content}}


@router.post("/ai/chat/stream")
async def chat_stream(req: ChatRequest, request: Request, db: AsyncSession = Depends(get_db)):
    await check_ai_rate(request)
    gw = _gw(req)

    async def event_gen():
        try:
            async for token in gw.stream_chat(req.messages, req.temperature, req.max_tokens):
                yield sse_data({"content": token})
        except Exception as e:  # noqa: BLE001
            yield sse_data({"error": str(e)[:200]})
        yield sse_done()

    return StreamingResponse(event_gen(), media_type="text/event-stream")


@router.post("/ai/explain")
async def explain(req: ExplainRequest, request: Request, db: AsyncSession = Depends(get_db)):
    await check_ai_rate(request)
    messages = build_messages(
        "code_explain",
        code=req.code,
        error_msg=req.error_msg or "",
        question=req.question or "",
    )
    gw = build_gateway(req.provider, req.api_key, req.base_url, req.model)
    content = await gw.chat(messages, temperature=0.3, max_tokens=1024)
    return {"code": 0, "message": "ok", "data": {"content": content}}


@router.post("/ai/detect")
async def detect(body: Dict[str, Any], request: Request):
    """自动识别厂商 + 探测可用模型列表。"""
    result = await auto_detect(body.get("base_url", "") or "", body.get("api_key", "") or "")
    return {"code": 0, "message": "ok", "data": result}
