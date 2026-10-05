"""错题本聚合、个性化学习路径推荐与 AI 学习规划师。聚合查询，无新增重型存储。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import (
    KnowledgePoint,
    LearningProgress,
    Problem,
    Submission,
    User,
)
from app.schemas.schemas import LearningPathOut, MistakeOut
from app.services.ai.factory import build_gateway_for_user
from app.services.ai.prompts import build_messages
from app.services.grading import _extract_json

router = APIRouter()


@router.get("/mistakes", response_model=list[MistakeOut])
async def list_mistakes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """学生的错题本：未完成（未通过或低分）提交，按时间倒序。"""
    rows = (
        await db.execute(
            select(Submission)
            .where(Submission.user_id == user.id)
            .where((Submission.passed == False) | (Submission.score < 60))  # noqa: E712
            .order_by(desc(Submission.submitted_at))
            .limit(100)
        )
    ).scalars().all()

    # 轻量补充知识点：用关联题目映射 problem_id -> knowledge_point
    prob_ids = {s.problem_id for s in rows if s.problem_id}
    kp_map: dict[int, str] = {}
    if prob_ids:
        probs = (
            await db.execute(select(Problem).where(Problem.id.in_(prob_ids)))
        ).scalars().all()
        kp_map = {p.id: p.knowledge_point for p in probs}

    result = []
    for s in rows:
        result.append(
            MistakeOut(
                submission_id=s.id,
                problem_id=s.problem_id,
                task_id=s.task_id,
                knowledge_point=kp_map.get(s.problem_id, "") if s.problem_id else "",
                code=s.code,
                error_msg=s.error_msg,
                ai_comment=s.ai_comment,
                score=s.score,
                mode=s.mode,
                submitted_at=s.submitted_at,
            )
        )
    return result


@router.get("/learning-path", response_model=LearningPathOut)
async def learning_path(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """基于学习进度的个性化学习路径与薄弱点。"""
    kps = (
        await db.execute(select(KnowledgePoint).order_by(KnowledgePoint.order_index))
    ).scalars().all()
    progress_rows = (
        await db.execute(
            select(LearningProgress).where(LearningProgress.user_id == user.id)
        )
    ).scalars().all()
    prog_map = {p.knowledge_point: p for p in progress_rows}

    weak_points: list[str] = []
    recommended: list[dict] = []
    for kp in kps:
        st = prog_map.get(kp.slug)
        status = st.status if st else "未学"
        acc = st.accuracy if st else 0.0
        if status != "已掌握":
            weak_points.append(kp.slug)
            recommended.append(
                {
                    "slug": kp.slug,
                    "title": kp.title,
                    "layer": kp.layer,
                    "difficulty": kp.difficulty,
                    "status": status,
                    "accuracy": acc,
                }
            )
    return LearningPathOut(
        user_id=user.id,
        recommended=recommended[:8],
        weak_points=weak_points[:8],
    )


# ---------------------------------------------------------------------------
# AI 学习规划师：自然语言 -> 个性化学习地图
# ---------------------------------------------------------------------------
class AdvisorRequest(BaseModel):
    major: str = ""      # 专业背景
    level: str = "零基础"  # 零基础 / 有编程经验 / 能写简单脚本
    goal: str = ""      # 学习目标，如"做量化分析"


@router.post("/learning-advisor")
async def learning_advisor(
    req: AdvisorRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """根据专业/水平/目标，让 AI 输出模块权重、分阶段计划与推荐案例。"""
    gw = await build_gateway_for_user(user.id, db, scene="case")
    messages = build_messages(
        "learning_advisor",
        major=req.major or "未指定",
        level=req.level or "零基础",
        goal=req.goal or "掌握 Python 基础并能解决实际问题",
    )
    try:
        content = await gw.chat(messages, temperature=0.5, max_tokens=1024)
        plan = _extract_json(content)
    except Exception:
        plan = None

    if not isinstance(plan, dict):
        # 降级：基于内置知识点给一个保守路径
        plan = {
            "summary": "AI 暂不可用，已为你生成通用学习路径：先打牢基础语法，再按兴趣选工具层深入。",
            "module_weights": {"基础语法": 40, "数据分析": 25, "可视化": 20, "办公自动化": 15},
            "steps": [
                {"phase": "第 1-2 周", "focus": "变量/条件循环/函数", "suggested_weeks": 2},
                {"phase": "第 3-4 周", "focus": "文件/异常/面向对象", "suggested_weeks": 2},
                {"phase": "第 5-8 周", "focus": "按专业方向选 Pandas/可视化/爬虫", "suggested_weeks": 4},
            ],
            "recommended_cases": ["简历词云", "销售数据透视", "爱心函数"],
            "tips": "每天坚持写 30 分钟代码，比一周突击 5 小时更有效。",
        }
    return {"code": 0, "message": "ok", "data": plan}


# ---------------------------------------------------------------------------
# 个人中心数据聚合：真实统计 + 最近提交历史
# ---------------------------------------------------------------------------
@router.get("/me/stats")
async def my_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """聚合当前用户的真实学习数据：提交数、通过率、代码行数、最近历史。"""
    base = select(Submission).where(Submission.user_id == user.id)

    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    passed = (await db.execute(
        select(func.count()).select_from(base.subquery()).where(Submission.status == "success")
    )).scalar_one()
    avg_score = (await db.execute(
        select(func.avg(Submission.score)).select_from(base.subquery())
    )).scalar_one() or 0.0
    track_a = (await db.execute(
        select(func.count()).select_from(base.subquery()).where(Submission.mode == "track_a")
    )).scalar_one()
    track_b = (await db.execute(
        select(func.count()).select_from(base.subquery()).where(Submission.mode == "track_b")
    )).scalar_one()

    # 最近 10 条提交
    recent_rows = (await db.execute(
        base.order_by(desc(Submission.submitted_at)).limit(10)
    )).scalars().all()

    prob_ids = {s.problem_id for s in recent_rows if s.problem_id}
    title_map: dict[int, str] = {}
    if prob_ids:
        probs = (await db.execute(select(Problem).where(Problem.id.in_(prob_ids)))).scalars().all()
        title_map = {p.id: p.title for p in probs}

    history = [
        {
            "id": s.id,
            "title": title_map.get(s.problem_id, f"提交 #{s.id}") if s.problem_id else f"作业提交 #{s.id}",
            "status": s.status,
            "score": s.score,
            "mode": s.mode,
            "submitted_at": s.submitted_at.isoformat() if s.submitted_at else "",
        }
        for s in recent_rows
    ]

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "total_submissions": total,
            "passed": passed,
            "pass_rate": round(passed / total * 100, 1) if total else 0,
            "avg_score": round(float(avg_score), 1),
            "track_a": track_a,
            "track_b": track_b,
            # AI 依赖度：track_b 占总提交比例。越低说明越独立，越高说明越依赖 AI。
            "ai_dependency": round(track_b / total * 100, 1) if total else 0,
            "history": history,
        },
    }
