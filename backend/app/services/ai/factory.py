"""AI 网关工厂：根据厂商 / 配置构建对应适配器。

- 无 Key 且无地址 -> Mock（降级可用）
- 指定 mock -> Mock
- 其余 -> OpenAI 兼容适配器（自动识别厂商与默认地址/模型）
"""
from __future__ import annotations

from sqlalchemy import select

from app.core.security import decrypt_text
from app.models.models import AIConfig
from app.services.ai.base import BaseAIGateway
from app.services.ai.detector import DEFAULT_BASE_URLS, DEFAULT_MODELS, detect_provider
from app.services.ai.mock import MockAdapter
from app.services.ai.openai_compatible import OpenAICompatibleAdapter

# 插件可在此注册自定义模型适配器：provider -> 适配器类（签名同 OpenAICompatibleAdapter）
MODEL_ADAPTERS: dict[str, type] = {}


def register_adapter(provider: str, cls: type) -> None:
    """插件注册自定义模型适配器。"""
    MODEL_ADAPTERS[provider] = cls


def unregister_adapter(provider: str) -> None:
    MODEL_ADAPTERS.pop(provider, None)


def build_gateway(
    provider: str | None,
    api_key: str | None,
    base_url: str | None = None,
    default_model: str | None = None,
    proxy: str | None = None,
) -> BaseAIGateway:
    provider = (provider or "auto").strip().lower()
    api_key = (api_key or "").strip()
    base_url = (base_url or "").strip()

    # 插件注册适配器优先
    if provider in MODEL_ADAPTERS:
        return MODEL_ADAPTERS[provider](api_key, base_url, default_model, proxy)

    # 降级：Mock
    if provider == "mock" or (not api_key and not base_url):
        return MockAdapter(default_model or "mock-python-tutor")

    # 自动识别厂商
    if provider in (None, "", "auto"):
        provider = detect_provider(base_url, api_key)

    resolved_url = base_url or DEFAULT_BASE_URLS.get(provider, "")
    model = default_model or DEFAULT_MODELS.get(provider, "")

    if provider == "custom":
        # 自定义：使用用户给定地址与模型（仍走 OpenAI 兼容协议）
        return OpenAICompatibleAdapter(api_key, resolved_url, model, proxy)

    return OpenAICompatibleAdapter(api_key, resolved_url, model, proxy)


async def build_gateway_for_user(user_id: int, db, scene: str = "") -> BaseAIGateway:
    """按用户已同步的云端 AI 配置构建网关；无配置则降级 Mock。

    scene 用于场景模型路由：AIConfig.scene_models 中若配置了 {"grade": "deepseek-chat"}，
    则批改场景使用该模型，未配置则回退 default_model。
    """
    cfg = (
        await db.execute(select(AIConfig).where(AIConfig.user_id == user_id))
    ).scalars().first()
    if not cfg or not cfg.api_key_encrypted:
        return MockAdapter(cfg.default_model if cfg else "mock-python-tutor")
    key = decrypt_text(cfg.api_key_encrypted)
    # 场景模型路由：优先取 scene_models[scene]，否则用 default_model
    model = cfg.default_model
    if scene and isinstance(cfg.scene_models, dict):
        model = cfg.scene_models.get(scene, model)
    return build_gateway(cfg.provider, key, cfg.base_url, model, cfg.proxy)


async def build_gateway_for_users(primary_id: int, fallback_id: int | None, db, scene: str = "") -> BaseAIGateway:
    """优先用 primary 用户配置；缺失则回退 fallback（如班级教师供给）。"""
    gw = await build_gateway_for_user(primary_id, db, scene=scene)
    if not isinstance(gw, MockAdapter):
        return gw
    if fallback_id and fallback_id != primary_id:
        gw2 = await build_gateway_for_user(fallback_id, db, scene=scene)
        if not isinstance(gw2, MockAdapter):
            return gw2
    return gw
