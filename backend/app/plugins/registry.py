"""插件注册表：启动时扫描 builtin 与外部目录，实例化并 setup。"""
from __future__ import annotations

import importlib
import os
import pkgutil
from typing import Dict

from app.plugins.base import PluginProtocol

PLUGINS: Dict[str, PluginProtocol] = {}


def _discover(package_name: str) -> None:
    try:
        package = importlib.import_module(package_name)
    except ModuleNotFoundError:  # noqa: BLE001
        return
    if not hasattr(package, "__path__"):
        return
    for mod in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package_name}.{mod.name}")
        for attr in dir(module):
            obj = getattr(module, attr)
            if (
                isinstance(obj, type)
                and issubclass(obj, PluginProtocol)
                and obj is not PluginProtocol
            ):
                inst = obj()
                if not inst.name:
                    continue
                PLUGINS[inst.name] = inst
                if inst.enabled:
                    try:
                        inst.setup()
                    except Exception:  # noqa: BLE001
                        # 单个插件失败不应阻断启动
                        pass


def load_plugins(extra_dir: str | None = None) -> None:
    """扫描内置插件目录与外部目录（extra_dir，可选）。"""
    _discover("app.plugins.builtin")
    if extra_dir and os.path.isdir(extra_dir):
        # 外部目录按文件动态导入（尽力而为，不强制）
        import sys

        for fname in os.listdir(extra_dir):
            if fname.endswith(".py") and not fname.startswith("_"):
                sys.path.insert(0, extra_dir)
                try:
                    importlib.import_module(fname[:-3])
                except Exception:  # noqa: BLE001
                    pass


def get_plugin_metadata() -> list[dict]:
    return [
        {
            "name": p.name,
            "display_name": p.name,
            "version": p.version,
            "description": p.description,
            "category": p.category,
            "enabled": p.enabled,
            "config": {},
        }
        for p in PLUGINS.values()
    ]
