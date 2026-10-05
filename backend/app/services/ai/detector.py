"""模型厂商自动识别：Base URL 域名匹配 + /v1/models 探测。"""
from __future__ import annotations

import httpx

# 厂商 -> 域名特征（用于 Base URL 前缀匹配）
_PROVIDER_DOMAINS: Dict[str, List[str]] = {
    "deepseek": ["deepseek.com", "api.deepseek.com"],
    "doubao": ["volcengine", "ark.cn", "byteintl"],
    "qwen": ["dashscope", "aliyun", "qwen"],
    "zhipu": ["zhipuai", "bigmodel", "open.bigmodel"],
    "openai": ["openai.com", "api.openai"],
    "ollama": ["localhost", "11434", "ollama"],
}

# 厂商 -> 默认 Base URL（含 /v1）
DEFAULT_BASE_URLS: Dict[str, str] = {
    "deepseek": "https://api.deepseek.com/v1",
    "doubao": "https://ark.cn-beijing.volcanicengine.com/api/v3",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "zhipu": "https://open.bigmodel.cn/api/paas/v4",
    "openai": "https://api.openai.com/v1",
    "ollama": "http://localhost:11434/v1",
}

# 厂商 -> 默认模型
DEFAULT_MODELS: Dict[str, str] = {
    "deepseek": "deepseek-chat",
    "doubao": "doubao-pro-4.0",
    "qwen": "qwen-plus",
    "zhipu": "glm-4",
    "openai": "gpt-3.5-turbo",
    "ollama": "llama3",
}


def detect_provider(base_url: str, api_key: str) -> str:
    """根据 Base URL 域名前缀匹配厂商。"""
    if not base_url:
        # 无地址：本地 ollama 概率高；但需 Key 时回退 custom
        return "ollama" if not api_key else "custom"
    low = base_url.lower()
    for provider, domains in _PROVIDER_DOMAINS.items():
        if any(d in low for d in domains):
            return provider
    return "custom"


async def auto_detect(base_url: str, api_key: str) -> Dict:
    """探测可用模型列表并自动识别厂商。

    返回 {provider, base_url, models}
    """
    provider = detect_provider(base_url, api_key)
    resolved_url = base_url or DEFAULT_BASE_URLS.get(provider, "")
    models: List[str] = []
    if resolved_url and api_key:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{resolved_url.rstrip('/')}/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                if resp.status_code == 200:
                    models = [m["id"] for m in resp.json().get("data", [])]
        except Exception:  # noqa: BLE001
            pass
    if not models and provider in DEFAULT_MODELS:
        models = [DEFAULT_MODELS[provider]]
    return {
        "provider": provider,
        "base_url": resolved_url,
        "models": models,
        "default_model": models[0] if models else DEFAULT_MODELS.get(provider, ""),
    }
