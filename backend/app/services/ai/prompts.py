"""提示词模板加载与渲染。模板置于 app/templates/prompts/，支持 {{var}} 注入。"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, List

import yaml

AI_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(AI_DIR)), "templates", "prompts")

_CACHE: Dict[str, dict] = {}

_VAR_RE = re.compile(r"{{\s*(\w+)\s*}}")


def load_prompt(name: str) -> dict:
    if name not in _CACHE:
        path = os.path.join(PROMPT_DIR, f"{name}.yaml")
        with open(path, "r", encoding="utf-8") as f:
            _CACHE[name] = yaml.safe_load(f)
    return _CACHE[name]


def render(template: str, **kwargs: Any) -> str:
    def repl(m: "re.Match[str]") -> str:
        key = m.group(1)
        val = kwargs.get(key, "")
        return "" if val is None else str(val)

    return _VAR_RE.sub(repl, template)


def build_messages(name: str, **kwargs: Any) -> List[Dict[str, str]]:
    """按场景名拼装 system/user 消息。"""
    p = load_prompt(name)
    messages: List[Dict[str, str]] = []
    if p.get("system"):
        messages.append({"role": "system", "content": render(p["system"], **kwargs)})
    messages.append({"role": "user", "content": render(p["user"], **kwargs)})
    return messages
