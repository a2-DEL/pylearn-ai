"""AI 陪练：代码评审 / 重构建议 + 对话式多轮陪练（SSE）。"""
from __future__ import annotations

import json
import re

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_optional_user
from app.models.models import User
from app.schemas.schemas import (
    ReviewRequest,
    ReviewResult,
    TutorRequest,
)
from app.services.ai.factory import build_gateway, build_gateway_for_user
from app.services.ai.prompts import build_messages
from app.services.ai.ratelimit import check_ai_rate
from app.services.ai.stream import sse_data, sse_done

router = APIRouter()


def _pick_gateway(req, user: User | None, db):
    """优先用请求显式传入的 provider/key（游客），否则用登录用户云端配置。"""
    if req.provider or req.api_key:
        return build_gateway(req.provider, req.api_key, req.base_url, req.model)
    return None  # 异步分支在路由内处理


async def _gateway_async(req, user: User | None, db):
    explicit = _pick_gateway(req, user, db)
    if explicit is not None:
        return explicit
    if user:
        return await build_gateway_for_user(user.id, db)
    return build_gateway(None, None, None, None)


def _extract_json(text: str) -> dict | None:
    """从模型输出中提取 JSON（兼容 ```json 围栏）。"""
    try:
        return json.loads(text)
    except Exception:  # noqa: BLE001
        pass
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:  # noqa: BLE001
            return None
    m2 = re.search(r"\{.*\}", text, re.DOTALL)
    if m2:
        try:
            return json.loads(m2.group(0))
        except Exception:  # noqa: BLE001
            return None
    return None


@router.post("/ai/review", response_model=ReviewResult)
async def review_code(
    req: ReviewRequest,
    request: Request,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    await check_ai_rate(request)
    gw = await _gateway_async(req, user, db)
    messages = build_messages("code_review", code=req.code, language=req.language or "python")
    content = await gw.chat(messages, temperature=0.3, max_tokens=1024)
    data = _extract_json(content)
    if data:
        return ReviewResult(
            comments=str(data.get("comments", content)),
            complexity=str(data.get("complexity", "")),
            risks=[str(x) for x in data.get("risks", [])],
            score=int(data.get("score", 0) or 0),
        )
    return ReviewResult(comments=content, score=0)


@router.post("/ai/tutor")
async def tutor_chat(
    req: TutorRequest,
    request: Request,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    await check_ai_rate(request)
    gw = await _gateway_async(req, user, db)
    sys_msg = build_messages("code_tutor", knowledge_point=req.knowledge_point or "")
    messages = list(sys_msg)
    for h in req.history:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": req.message})
    content = await gw.chat(messages, temperature=0.5, max_tokens=1024)
    return {"code": 0, "message": "ok", "data": {"content": content}}


@router.post("/ai/tutor/stream")
async def tutor_stream(
    req: TutorRequest,
    request: Request,
    user: User | None = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db),
):
    await check_ai_rate(request)
    gw = await _gateway_async(req, user, db)
    sys_msg = build_messages("code_tutor", knowledge_point=req.knowledge_point or "")
    messages = list(sys_msg)
    for h in req.history:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": req.message})

    async def event_gen():
        try:
            async for token in gw.stream_chat(messages, temperature=0.5, max_tokens=1024):
                yield sse_data({"content": token})
        except Exception as e:  # noqa: BLE001
            yield sse_data({"error": str(e)[:200]})
        yield sse_done()

    return StreamingResponse(event_gen(), media_type="text/event-stream")
