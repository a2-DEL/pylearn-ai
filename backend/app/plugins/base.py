"""插件协议：所有内置/第三方插件需实现 PluginProtocol。"""
from __future__ import annotations

from abc import ABC, abstractmethod


class PluginProtocol(ABC):
    name: str = ""          # 唯一标识
    version: str = "0.1.0"
    category: str = "model"  # model / knowledge / eval
    enabled: bool = True
    description: str = ""

    @abstractmethod
    def setup(self) -> None:
        """注册适配器 / 钩子到全局 registry（仅当 enabled）。"""
        ...

    def teardown(self) -> None:
        """卸载钩子。"""
        ...
