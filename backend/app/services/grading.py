"""作业自动批改服务：测试用例执行 + AI 三维评审 + 相似度预警。

- 测试用例执行：在受控子进程中运行学生代码，按 {input(调用表达式), expected} 逐条校验
- AI 评审：复用 homework_grade 提示词，给出规范度/可读性/算法效率综合评分与评语
- 相似度预警：与同任务其他通过的提交做行级重叠比对，超阈值标记（防抄袭占位）
- 降级：AI 不可用时以测试用例通过情况给出基础分
"""
from __future__ import annotations

import asyncio
import json
import os
import tempfile
import time
from typing import Any, Dict, List

from sqlalchemy import select

from app.core.config import settings
from app.models.models import Submission
from app.services.ai.factory import build_gateway_for_users
from app.services.ai.prompts import build_messages


# ---------------------------------------------------------------------------
# 测试用例执行（受控子进程，绕过公共沙箱的危险预检以允许 eval/exec）
# ---------------------------------------------------------------------------
def _build_harness(user_code: str, test_cases: List[Dict[str, Any]]) -> str:
    cases_json = json.dumps(test_cases, ensure_ascii=False)
    return (
        "import json, importlib.util, sys\n"
        "spec = importlib.util.spec_from_file_location('solution', 'solution.py')\n"
        "m = importlib.util.module_from_spec(spec)\n"
        "try:\n"
        "    spec.loader.exec_module(m)\n"
        "except Exception as e:\n"
        "    print('__GRADING__' + json.dumps([{'passed': False, 'error': '代码执行错误: ' + str(e)[:300]}]))\n"
        "    sys.exit(0)\n"
        "ns = vars(m)\n"
        "cases = json.loads(__import__('sys').argv[1])\n"
        "results = []\n"
        "for c in cases:\n"
        "    try:\n"
        "        res = eval(c['input'], ns)\n"
        "        ok = str(res) == str(c['expected'])\n"
        "        results.append({'passed': ok, 'result': repr(res), 'expected': c['expected']})\n"
        "    except Exception as e:\n"
        "        results.append({'passed': False, 'error': str(e)[:300]})\n"
        "print('__GRADING__' + json.dumps(results))\n"
    )


async def run_test_cases(code: str, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """执行测试用例，返回逐条结果。无用例返回空列表。"""
    if not test_cases:
        return []
    with tempfile.TemporaryDirectory() as tmp:
        sol_path = os.path.join(tmp, "solution.py")
        har_path = os.path.join(tmp, "harness.py")
        with open(sol_path, "w", encoding="utf-8") as f:
            f.write(code)
        with open(har_path, "w", encoding="utf-8") as f:
            f.write(_build_harness(code, test_cases))
        start = time.time()
        try:
            proc = await asyncio.create_subprocess_exec(
                "python", har_path, json.dumps(test_cases, ensure_ascii=False),
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=tmp,
            )
            out, err = await asyncio.wait_for(proc.communicate(), timeout=settings.SANDBOX_TIMEOUT)
        except asyncio.TimeoutError:
            return [{"passed": False, "error": f"执行超时（>{settings.SANDBOX_TIMEOUT}s）"}]
        except Exception as e:  # noqa: BLE001
            return [{"passed": False, "error": f"无法运行代码：{e}"}]
        run_time = round(time.time() - start, 3)
        stdout = out.decode("utf-8", "replace")
        marker = "__GRADING__"
        for line in stdout.splitlines():
            if marker in line:
                try:
                    return json.loads(line.split(marker, 1)[1])
                except Exception:  # noqa: BLE001
                    break
        return [{"passed": False, "error": (err.decode("utf-8", "replace") or "无输出")[:300]}]


# ---------------------------------------------------------------------------
# 相似度预警（行级重叠）
# ---------------------------------------------------------------------------
async def similarity_flag(db, code: str, task_id: int, user_id: int) -> bool:
    rows = (
        await db.execute(
            select(Submission).where(
                Submission.task_id == task_id,
                Submission.passed.is_(True),
                Submission.user_id != user_id,
            )
        )
    ).scalars().all()
    if not rows:
        return False
    a_lines = {ln.strip() for ln in code.splitlines() if ln.strip()}
    if not a_lines:
        return False
    for other in rows:
        b_lines = {ln.strip() for ln in other.code.splitlines() if ln.strip()}
        if not b_lines:
            continue
        overlap = len(a_lines & b_lines) / len(a_lines | b_lines)
        if overlap > 0.85:
            return True
    return False


# ---------------------------------------------------------------------------
# 综合批改
# ---------------------------------------------------------------------------
async def grade_submission(
    db, *, code: str, task, student_id: int, teacher_id: int | None
) -> Dict[str, Any]:
    """执行完整批改流程，返回结果字典。"""
    test_detail = await run_test_cases(code, task.test_cases or [])
    passed = bool(test_detail) and all(t.get("passed") for t in test_detail)
    error_msg = ""
    if test_detail and not passed:
        error_msg = next((t.get("error", "") for t in test_detail if not t.get("passed")), "存在未通过用例")

    similar_flag = await similarity_flag(db, code, task.id, student_id)

    # AI 三维评审
    ai_score = 100 if passed else 0
    ai_comment = "已通过全部测试用例。" if passed else "存在未通过的测试用例，请检查实现。"
    try:
        gw = await build_gateway_for_users(student_id, teacher_id, db, scene="grade")
        messages = build_messages(
            "homework_grade", title=task.title, description=task.description, code=code
        )
        content = await gw.chat(messages, temperature=0.3, max_tokens=1024)
        parsed = _extract_json(content)
        if parsed and "score" in parsed:
            ai_score = int(parsed.get("score", ai_score))
            ai_comment = parsed.get("comment", ai_comment)
    except Exception:  # noqa: BLE001
        # 降级：以测试结果给基础分
        ai_score = 100 if passed else 0

    # 最终分：正确性为主，质量为辅
    if test_detail:
        final_score = round((100 if passed else 0) * 0.6 + ai_score * 0.4)
    else:
        final_score = ai_score  # 无用例则完全参考 AI 评审

    return {
        "status": "success" if passed else "failed",
        "passed": passed,
        "score": max(0, min(100, final_score)),
        "run_time": 0.0,
        "error_msg": error_msg,
        "ai_comment": ai_comment,
        "test_detail": test_detail,
        "similar_flag": similar_flag,
    }


def _extract_json(text: str) -> Dict[str, Any] | None:
    """从模型输出中提取首个 JSON 对象。"""
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])
    except Exception:  # noqa: BLE001
        return None
    return None
