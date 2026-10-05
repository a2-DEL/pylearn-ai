"""SSE 流式辅助：将文本分块格式化为 event-stream。"""
from __future__ import annotations

import json


def sse_data(payload: dict) -> str:
    """构造一行 SSE data（data: <json>\n\n）。"""
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def sse_done() -> str:
    return "data: [DONE]\n\n"
