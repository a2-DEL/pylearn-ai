"""AI 配置中心接口：CRUD + AES 加密存储 + 测试连接。

- 游客（user_id=0）/ 个人用户均可存储；API Key 入库即密文，接口只回显后 4 位。
- 测试连接：用请求体中的配置构建网关并 check_connection（不下发完整 Key）。
"""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_optional_user
from app.core.exceptions import AppError
from app.core.security import encrypt_text, mask_api_key
from app.models.models import AIConfig, User
from app.schemas.schemas import AIConfigCreate, AIConfigOut, AIConfigUpdate
from app.services.ai.factory import build_gateway

router = APIRouter()


def _to_out(cfg: AIConfig) -> AIConfigOut:
    return AIConfigOut(
        id=cfg.id,
        user_id=cfg.user_id,
        provider=cfg.provider,
        api_key_masked=mask_api_key(_maybe_decrypt(cfg.api_key_encrypted)),
        base_url=cfg.base_url,
        default_model=cfg.default_model,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        is_synced=cfg.is_synced,
        scene_models=cfg.scene_models or {},
        proxy=cfg.proxy,
    )


def _maybe_decrypt(cipher: str) -> str:
    if not cipher:
        return ""
    # 仅用于脱敏回显，解密后取后 4 位
    try:
        from app.core.security import decrypt_text

        return decrypt_text(cipher)
    except Exception:  # noqa: BLE001
        return ""


@router.post("/ai-config", response_model=AIConfigOut)
async def create_config(req: AIConfigCreate, user: User | None = Depends(get_optional_user), db: AsyncSession = Depends(get_db)):
    encrypted = encrypt_text(req.api_key) if req.api_key else ""
    cfg = AIConfig(
        user_id=user.id if user else 0,  # 登录用户写入云端；游客仅本地
        provider=req.provider,
        api_key_encrypted=encrypted,
        base_url=req.base_url,
        default_model=req.default_model,
        temperature=req.temperature,
        max_tokens=req.max_tokens,
        is_synced=req.is_synced,
        scene_models=req.scene_models,
        proxy=req.proxy,
    )
    db.add(cfg)
    await db.commit()
    await db.refresh(cfg)
    return _to_out(cfg)


@router.get("/ai-config", response_model=List[AIConfigOut])
async def list_configs(
    user_id: int = Query(0), user: User | None = Depends(get_optional_user), db: AsyncSession = Depends(get_db)
):
    effective = user.id if user else user_id
    rows = (await db.execute(select(AIConfig).where(AIConfig.user_id == effective))).scalars().all()
    return [_to_out(r) for r in rows]


@router.get("/ai-config/{cfg_id}", response_model=AIConfigOut)
async def get_config(cfg_id: int, db: AsyncSession = Depends(get_db)):
    cfg = (await db.get(AIConfig, cfg_id))
    if not cfg:
        raise AppError("配置不存在", code=404)
    return _to_out(cfg)


@router.put("/ai-config/{cfg_id}", response_model=AIConfigOut)
async def update_config(cfg_id: int, req: AIConfigUpdate, db: AsyncSession = Depends(get_db)):
    cfg = await db.get(AIConfig, cfg_id)
    if not cfg:
        raise AppError("配置不存在", code=404)
    data = req.model_dump(exclude_unset=True)
    if "api_key" in data and data["api_key"]:
        cfg.api_key_encrypted = encrypt_text(data["api_key"])
    for k, v in data.items():
        if k == "api_key":
            continue
        setattr(cfg, k, v)
    await db.commit()
    await db.refresh(cfg)
    return _to_out(cfg)


@router.delete("/ai-config/{cfg_id}")
async def delete_config(cfg_id: int, db: AsyncSession = Depends(get_db)):
    cfg = await db.get(AIConfig, cfg_id)
    if not cfg:
        raise AppError("配置不存在", code=404)
    await db.delete(cfg)
    await db.commit()
    return {"code": 0, "message": "已删除"}


@router.post("/ai-config/test")
async def test_connection(body: Dict[str, Any]):
    """测试连接：根据请求体配置构建网关并探测。不返回完整 Key。"""
    provider = body.get("provider") or "auto"
    api_key = body.get("api_key") or ""
    base_url = body.get("base_url") or ""
    default_model = body.get("default_model") or ""
    proxy = body.get("proxy") or None
    gw = build_gateway(provider, api_key, base_url, default_model, proxy)
    success, message = await gw.check_connection()
    models = await gw.list_models() if success else []
    return {
        "code": 0,
        "message": "ok",
        "data": {"success": success, "message": message, "models": models},
    }
