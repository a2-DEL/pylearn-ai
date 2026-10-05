"""专业教学方案定制 + AI 协作编程（Prompt 训练）评分接口。

- /plans/teaching: 自然语言培养目标 -> AI 输出（模块权重/分阶段计划/案例包/考核建议）
- /plans/prompt-train: 学生写 Prompt -> 调其配置模型生成代码 -> 四维评分 + 评语
- /plans/debug-train: 双轨 B 模式 3，AI 埋雷代码，学生找 bug 修复
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.exceptions import AppError
from app.models.models import User
from app.schemas.schemas import PromptTrainRequest, TeachingPlanRequest
from app.services.ai.debug_challenges import DEBUG_CHALLENGES
from app.services.ai.decompose_challenges import DECOMPOSE_CHALLENGES
from app.services.ai.factory import build_gateway, build_gateway_for_user
from app.services.ai.interview_questions import INTERVIEW_QUESTIONS
from app.services.ai.prompts import build_messages
from app.services.grading import _extract_json, run_test_cases
from app.services.sandbox.factory import get_sandbox


router = APIRouter()


@router.post("/plans/teaching")
async def teaching_plan(req: TeachingPlanRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    gw = await build_gateway_for_user(user.id, db)
    messages = build_messages("teaching_plan", major=req.major, goal=req.goal, style=req.style)
    content = await gw.chat(messages, temperature=0.6, max_tokens=2048)
    plan = _extract_json(content)
    if not isinstance(plan, dict):
        raise AppError("AI 未能生成有效方案，请重试", code=502)
    return {"code": 0, "message": "ok", "data": plan}


@router.post("/plans/prompt-train")
async def prompt_train(req: PromptTrainRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """轨道 B 模式 2：Prompt 编程训练评分。支持游客明文 Key 或登录用户云端配置。"""
    if req.api_key:
        gw = build_gateway(req.provider, req.api_key, req.base_url, req.model)
    else:
        gw = await build_gateway_for_user(user.id, db)

    # 1) 用学生 Prompt 生成代码
    gen_messages = [
        {
            "role": "system",
            "content": "你是 Python 代码生成器，严格按照用户指令生成可运行代码，只输出代码，不要解释。",
        },
        {"role": "user", "content": f"需求背景：{req.requirement}\n学生指令：{req.prompt}"},
    ]
    generated_code = await gw.chat(gen_messages, temperature=0.2, max_tokens=1024)

    # 2) 评估 Prompt 与代码
    eval_messages = build_messages("prompt_train", requirement=req.requirement, prompt=req.prompt, code=generated_code)
    eval_content = await gw.chat(eval_messages, temperature=0.3, max_tokens=1024)
    scored = _extract_json(eval_content)
    if not isinstance(scored, dict):
        scored = {"comment": "AI 评估不可用，请参考生成代码自行检查。",
                  "clarity": 0, "boundary": 0, "correctness": 0, "efficiency": 0}

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "generated_code": generated_code,
            "score": {
                "clarity": scored.get("clarity", 0),
                "boundary": scored.get("boundary", 0),
                "correctness": scored.get("correctness", 0),
                "efficiency": scored.get("efficiency", 0),
                "comment": scored.get("comment", ""),
            },
        },
    }


# ---------------------------------------------------------------------------
# 双轨 B 模式 3：代码审查找 bug 训练
# ---------------------------------------------------------------------------
class DebugSubmitRequest(BaseModel):
    code: str  # 学生修复后的完整代码


def _public_challenge(c: dict) -> dict:
    """对外暴露的挑战：不泄露参考答案与 bug 清单。"""
    return {
        "id": c["id"],
        "title": c["title"],
        "difficulty": c["difficulty"],
        "description": c["description"],
        "buggy_code": c["buggy_code"],
    }


@router.get("/plans/debug-train")
async def list_debug_challenges(user: User = Depends(get_current_user)):
    """列出所有找 bug 训练题。"""
    return {
        "code": 0,
        "message": "ok",
        "data": [_public_challenge(c) for c in DEBUG_CHALLENGES],
    }


@router.post("/plans/debug-train/{challenge_id}/submit")
async def submit_debug_fix(
    challenge_id: int,
    req: DebugSubmitRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """学生提交修复后的代码：先跑测试用例，再让 AI 对照参考答案评审。"""
    challenge = next((c for c in DEBUG_CHALLENGES if c["id"] == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="训练题不存在")

    # 1) 跑测试用例（用 grading 的 harness，与作业批改同一套执行器）
    test_detail = await run_test_cases(req.code, challenge["test_cases"])
    passed = bool(test_detail) and all(t.get("passed") for t in test_detail)

    # 2) AI 评审（学生自己的网关；失败则降级为仅用测试结果）
    gw = await build_gateway_for_user(user.id, db, scene="review")
    ai_score = 100 if passed else 0
    comment = "全部测试用例通过。" if passed else "存在未通过的测试用例。"
    bugs_found = 0
    bugs_missed: list[str] = []
    try:
        messages = build_messages(
            "debug_train",
            title=challenge["title"],
            buggy_code=challenge["buggy_code"],
            reference_code=challenge["reference_code"],
            student_code=req.code,
        )
        content = await gw.chat(messages, temperature=0.3, max_tokens=1024)
        parsed = _extract_json(content) or {}
        ai_score = int(parsed.get("score", ai_score))
        comment = str(parsed.get("comment", comment))
        bugs_found = int(parsed.get("bugs_found", 0))
        bugs_missed = [str(x) for x in parsed.get("bugs_missed", [])]
    except Exception:
        # Mock 或网络异常：以测试结果为准
        pass

    final_score = max(0, min(100, ai_score if not test_detail else int((100 if passed else 0) * 0.6 + ai_score * 0.4)))

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "passed": passed,
            "score": final_score,
            "bugs_found": bugs_found,
            "bugs_missed": bugs_missed,
            "test_detail": test_detail,
            "comment": comment,
            "reference_revealed": passed,  # 测试通过才展示参考答案
            "reference_code": challenge["reference_code"] if passed else "",
        },
    }


# ---------------------------------------------------------------------------
# 双轨 B 模式 1：需求拆解训练
# ---------------------------------------------------------------------------
class DecomposeSubmitRequest(BaseModel):
    breakdown: str  # 学生写的实现步骤拆解


@router.get("/plans/decompose-train")
async def list_decompose(user: User = Depends(get_current_user)):
    """列出需求拆解训练题。"""
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"id": c["id"], "title": c["title"], "difficulty": c["difficulty"], "requirement": c["requirement"]}
            for c in DECOMPOSE_CHALLENGES
        ],
    }


@router.post("/plans/decompose-train/{challenge_id}/submit")
async def submit_decompose(
    challenge_id: int,
    req: DecomposeSubmitRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """学生提交自己的拆解，AI 给出标准拆解并对比点评。"""
    challenge = next((c for c in DECOMPOSE_CHALLENGES if c["id"] == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="训练题不存在")
    if not req.breakdown.strip():
        raise AppError("请先写下你的实现步骤拆解", code=400)

    gw = await build_gateway_for_user(user.id, db, scene="case")
    try:
        messages = build_messages(
            "decompose_train",
            requirement=challenge["requirement"],
            student_breakdown=req.breakdown,
        )
        content = await gw.chat(messages, temperature=0.4, max_tokens=1024)
        parsed = _extract_json(content) or {}
    except Exception:
        parsed = {}

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "standard_steps": parsed.get("standard_steps", ["AI 暂不可用，请自己再想想：输入是什么？处理什么？输出什么？"]),
            "gaps": parsed.get("gaps", []),
            "score": int(parsed.get("score", 0) or 0),
            "comment": parsed.get("comment", ""),
        },
    }


# ---------------------------------------------------------------------------
# 双轨 B 模式 4：结对编程（学生写一半，AI 补全）
# ---------------------------------------------------------------------------
class PeerProgramRequest(BaseModel):
    requirement: str
    student_code: str


@router.post("/plans/peer-program")
async def peer_program(
    req: PeerProgramRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """学生写框架/TODO，AI 补全剩余代码。"""
    gw = await build_gateway_for_user(user.id, db, scene="case")
    completed = ""
    try:
        messages = build_messages(
            "peer_programming",
            requirement=req.requirement,
            student_code=req.student_code,
        )
        completed = await gw.chat(messages, temperature=0.2, max_tokens=1024)
    except Exception:
        pass

    if not completed.strip():
        completed = "# AI 暂不可用，请手动完成 TODO 部分\n" + req.student_code

    return {"code": 0, "message": "ok", "data": {"completed_code": completed}}


# ---------------------------------------------------------------------------
# 企业 AI Coding 面试真题库
# ---------------------------------------------------------------------------
class InterviewSubmitRequest(BaseModel):
    prompt: str  # 学生写给 AI 的 Prompt


@router.get("/plans/interview/list")
async def list_interview_questions(user: User = Depends(get_current_user)):
    """列出所有面试真题（不暴露测试用例）。"""
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {
                "id": q["id"],
                "title": q["title"],
                "difficulty": q["difficulty"],
                "category": q["category"],
                "requirement": q["requirement"],
            }
            for q in INTERVIEW_QUESTIONS
        ],
    }


@router.post("/plans/interview/{qid}/submit")
async def submit_interview(
    qid: int,
    req: InterviewSubmitRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """学生提交 Prompt，AI 生成代码 -> 沙箱跑隐藏测试 -> 出面试报告。"""
    q = next((x for x in INTERVIEW_QUESTIONS if x["id"] == qid), None)
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    if not req.prompt.strip():
        raise AppError("请先写下你给 AI 的指令（Prompt）", code=400)

    # 1) 让 AI 按学生 Prompt 生成代码
    gw = await build_gateway_for_user(user.id, db, scene="case")
    gen_messages = [
        {
            "role": "system",
            "content": "你是 Python 代码生成器。严格按指令输出一个可运行的 .py 代码块，包含题目要求的函数定义，不要解释，不要 markdown 包裹。",
        },
        {
            "role": "user",
            "content": f"业务需求：{q['requirement']}\n我的指令：{req.prompt}",
        },
    ]
    generated = await gw.chat(gen_messages, temperature=0.2, max_tokens=1024)
    # 去掉可能的 markdown 代码围栏
    generated = generated.strip().removeprefix("```python").removeprefix("```").removesuffix("```").strip()

    # 2) 拼测试脚本丢沙箱跑
    test_lines = []
    for c in q["test_cases"]:
        test_lines.append(
            f"try:\n"
            f"    _r = {c['call']}\n"
            f"    _e = {c['expected']}\n"
            f"    if _r == _e: print('PASS {c['call']}')\n"
            f"    else: print(f'FAIL {c['call']} got={{_r!r}} want={{_e!r}}')\n"
            f"except Exception as _ex:\n"
            f"    print(f'ERROR {c['call']} -> {{_ex}}')"
        )
    script = generated + "\n\n# --- hidden tests ---\n" + "\n".join(test_lines)

    sandbox = get_sandbox()
    run = await sandbox.run(script, timeout=10, enable_network=False)
    out = (run.get("stdout") or "") + (run.get("stderr") or "")

    passed = sum(1 for line in out.splitlines() if line.startswith("PASS"))
    total = len(q["test_cases"])
    case_results = []
    for c in q["test_cases"]:
        marker_pass = f"PASS {c['call']}"
        case_results.append({
            "call": c["call"],
            "expected": c["expected"],
            "passed": marker_pass in out,
        })

    # 3) Prompt 关键词命中（考察学生是否想到了边界）
    prompt_lower = req.prompt.lower()
    hints_hit = [kw for kw in q["reference_keywords"] if kw.lower() in prompt_lower]

    # 4) 综合分：测试通过率 70% + 关键词命中 30%
    score = int(passed / total * 70 + len(hints_hit) / len(q["reference_keywords"]) * 30)

    # 5) AI 评语（可选，失败时给改进建议）
    comment = ""
    if passed < total:
        missed = [c["call"] for c, r in zip(q["test_cases"], case_results) if not r["passed"]]
        comment = f"{len(missed)}/{total} 个用例未通过：{', '.join(missed)}。"
        if len(hints_hit) < len(q["reference_keywords"]):
            missed_kw = [kw for kw in q["reference_keywords"] if kw not in hints_hit]
            comment += f" Prompt 里没提到：{', '.join(missed_kw)}——下次把这些边界写清楚，AI 一次就写对。"

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "generated_code": generated,
            "case_results": case_results,
            "passed": passed,
            "total": total,
            "hints_hit": hints_hit,
            "hints_total": q["reference_keywords"],
            "score": score,
            "comment": comment,
            "sandbox_stdout": out,
        },
    }
