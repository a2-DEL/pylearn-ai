"""特性开关：从环境变量 FEATURE_<NAME> 读取（true/1 开启）。"""
from __future__ import annotations

import os


def is_on(flag: str, default: bool = False) -> bool:
    """读取特性开关，例如 is_on('community') -> 环境变量 FEATURE_COMMUNITY。"""
    env = os.getenv(f"FEATURE_{flag.upper()}")
    if env is None:
        return default
    return env.strip().lower() in ("1", "true", "yes", "on")
