"""内置示例：注册一个名为 demo 的模型适配器（基于 Mock 降级）。

展示「模型插件」机制：setup 时把 provider=demo 注入工厂，
build_gateway 将优先使用已注册适配器。
"""
from __future__ import annotations

from app.plugins.base import PluginProtocol
from app.services.ai.factory import register_adapter
from app.services.ai.mock import MockAdapter


class DemoModelAdapter(MockAdapter):
    def __init__(self, api_key=None, base_url=None, model=None, proxy=None):
        super().__init__(model or "demo-model")


class DemoModelPlugin(PluginProtocol):
    name = "demo-model"
    version = "0.1.0"
    category = "model"
    description = "示例模型插件：注册 demo 提供商，使用本地 Mock 适配器演示动态注入。"

    def setup(self) -> None:
        register_adapter("demo", DemoModelAdapter)

    def teardown(self) -> None:
        from app.services.ai.factory import unregister_adapter

        unregister_adapter("demo")
