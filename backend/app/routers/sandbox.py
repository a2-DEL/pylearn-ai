"""代码运行接口。降级可用：无需 AI 也能纯编程练习。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.models import Submission
from app.schemas.schemas import RunCodeRequest, RunCodeResult
from app.services.sandbox.factory import get_sandbox

router = APIRouter()


@router.post("/sandbox/run", response_model=RunCodeResult)
async def run_code(req: RunCodeRequest, db: AsyncSession = Depends(get_db)) -> RunCodeResult:
    sandbox = get_sandbox()
    result = await sandbox.run(
        req.code, timeout=settings.SANDBOX_TIMEOUT, enable_network=req.enable_network
    )

    # 落库提交记录（游客 user_id=0）
    sub = Submission(
        problem_id=req.problem_id,
        user_id=0,
        code=req.code,
        status="success" if result["success"] else "failed",
        run_time=result["run_time"],
        error_msg=result.get("error") or result.get("stderr") or "",
    )
    db.add(sub)
    await db.commit()

    return RunCodeResult(**result)
