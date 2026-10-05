"""种子数据：幂等写入知识点与题目。

按 slug/标题 upsert：重复启动不重复插入；新增的知识点与题目会在下次启动时补齐，
已存在的记录保持用户原数据不动。
"""
from __future__ import annotations

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.models import KnowledgePoint, Problem
from app.seed.data import KNOWLEDGE_POINTS, PROBLEMS


async def seed_all() -> None:
    async with SessionLocal() as session:
        # 知识点：按 slug upsert
        existing_kps = (await session.execute(select(KnowledgePoint))).scalars().all()
        kp_map = {kp.slug: kp for kp in existing_kps}
        for kp in KNOWLEDGE_POINTS:
            slug = kp["slug"]
            if slug in kp_map:
                row = kp_map[slug]
                # 仅更新标题/内容/示例等教学字段，不动用户掌握状态
                for field in ("title", "content", "example_code", "order_index",
                              "layer", "category", "difficulty"):
                    if field in kp:
                        setattr(row, field, kp[field])
            else:
                session.add(KnowledgePoint(**kp))

        # 题目：按 title upsert
        existing_ps = (await session.execute(select(Problem))).scalars().all()
        p_map = {p.title: p for p in existing_ps}
        for p in PROBLEMS:
            title = p["title"]
            if title in p_map:
                row = p_map[title]
                for field in ("description", "difficulty", "knowledge_point",
                              "example_input", "example_output", "test_cases", "hints"):
                    if field in p:
                        setattr(row, field, p[field])
            else:
                session.add(Problem(**p))

        await session.commit()
