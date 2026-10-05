"""插件市场：列出已加载插件，支持启用 / 停用（仅教师）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_teacher
from app.models.models import Plugin, User
from app.plugins.registry import PLUGINS
from app.schemas.schemas import PluginOut, PluginUpdate

router = APIRouter()


@router.get("/plugins", response_model=list[PluginOut])
async def list_plugins(
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    """列出已加载插件及其当前启用状态（合并 DB 持久化）。"""
    db_rows = (
        await db.execute(select(Plugin).where(Plugin.name.in_(list(PLUGINS.keys()))))
    ).scalars().all()
    enabled_db = {r.name: r.enabled for r in db_rows}
    result = []
    for name, inst in PLUGINS.items():
        enabled = enabled_db.get(name, inst.enabled)
        result.append(
            PluginOut(
                name=name,
                display_name=inst.name,
                version=inst.version,
                description=inst.description,
                category=inst.category,
                enabled=enabled,
                config={},
            )
        )
    return result


@router.put("/plugins/{name}", response_model=PluginOut)
async def update_plugin(
    name: str,
    req: PluginUpdate,
    user: User = Depends(require_teacher),
    db: AsyncSession = Depends(get_db),
):
    inst = PLUGINS.get(name)
    if not inst:
        from app.core.exceptions import AppError

        raise AppError("插件不存在", code=404)
    if req.enabled is not None:
        inst.enabled = req.enabled
        if req.enabled:
            try:
                inst.setup()
            except Exception:  # noqa: BLE001
                pass
        else:
            try:
                inst.teardown()
            except Exception:  # noqa: BLE001
                pass
    # 持久化到 Plugin 表
    row = (
        await db.execute(select(Plugin).where(Plugin.name == name))
    ).scalars().first()
    if row:
        row.enabled = inst.enabled
        if req.config is not None:
            row.config = req.config
    else:
        row = Plugin(
            name=name,
            display_name=inst.name,
            version=inst.version,
            description=inst.description,
            category=inst.category,
            enabled=inst.enabled,
            config=req.config or {},
        )
        db.add(row)
    await db.commit()
    return PluginOut(
        name=name,
        display_name=inst.name,
        version=inst.version,
        description=inst.description,
        category=inst.category,
        enabled=inst.enabled,
        config=req.config or {},
    )
