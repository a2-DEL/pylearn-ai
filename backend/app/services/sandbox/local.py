"""本地受限沙箱：受限制子进程兜底实现（无 Docker 环境可用）。

安全策略（兜底，不能等同于容器隔离）：
- 危险代码黑名单预检，命中即拦截；
- 在独立临时目录运行，仅标准输入输出，不挂载宿主机目录；
- 超时强制终止；
- 输出长度截断，避免刷屏。
Windows 无 resource 模块，内存限制以文档说明；容器版(Docker)补充资源配额。
"""
from __future__ import annotations

import asyncio
import os
import sys
import tempfile
import time
from typing import Any, Dict

from app.core.config import settings
from app.core.security import check_dangerous_code
from app.services.sandbox.base import SandboxBase


class LocalSandbox(SandboxBase):
    async def run(
        self, code: str, timeout: int = 10, enable_network: bool = False
    ) -> Dict[str, Any]:
        # 1. 危险代码预检
        danger = check_dangerous_code(code)
        if danger:
            return {
                "stdout": "",
                "stderr": "",
                "run_time": 0.0,
                "success": False,
                "error": danger,
            }

        # 2. 写入临时目录
        with tempfile.TemporaryDirectory() as tmp:
            main_path = os.path.join(tmp, "main.py")
            with open(main_path, "w", encoding="utf-8") as f:
                f.write(code)

            start = time.time()
            try:
                proc = await asyncio.create_subprocess_exec(
                    sys.executable,
                    main_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=tmp,
                    env={**os.environ, "PYTHONSAFEPATH": "1"},
                )
            except Exception as e:  # pragma: no cover
                return {
                    "stdout": "",
                    "stderr": "",
                    "run_time": 0.0,
                    "success": False,
                    "error": f"无法启动 Python 解释器：{e}",
                }

            try:
                out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return {
                    "stdout": "",
                    "stderr": "",
                    "run_time": round(time.time() - start, 3),
                    "success": False,
                    "error": f"执行超时（>{timeout}s），已强制终止。可能陷入死循环或网络被禁用。",
                }

            run_time = round(time.time() - start, 3)
            stdout = out.decode("utf-8", "replace")[: settings.SANDBOX_MAX_OUTPUT]
            stderr = err.decode("utf-8", "replace")[: settings.SANDBOX_MAX_OUTPUT]
            success = proc.returncode == 0

            return {
                "stdout": stdout,
                "stderr": stderr,
                "run_time": run_time,
                "success": success,
                "error": "" if success else (stderr or f"进程退出码 {proc.returncode}"),
            }
