"""插件包入口。"""
from app.plugins.registry import get_plugin_metadata, load_plugins

__all__ = ["load_plugins", "get_plugin_metadata"]
