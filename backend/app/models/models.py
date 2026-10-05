"""ORM 模型（SQLAlchemy 2.0 风格，Mapped 注解）。遵循规范第七章表结构。"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    """用户表（阶段二完整启用，MVP 保留结构）。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), default="")
    email: Mapped[str | None] = mapped_column(String(120), unique=True, nullable=True)
    roles: Mapped[str] = mapped_column(String(120), default="student")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class AIConfig(Base):
    """AI 配置表：API Key 全链路密文存储。"""

    __tablename__ = "ai_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, default=0)  # 0 = 游客/本地
    provider: Mapped[str] = mapped_column(String(50), default="auto")
    api_key_encrypted: Mapped[str] = mapped_column(Text, default="")
    base_url: Mapped[str] = mapped_column(String(255), default="")
    default_model: Mapped[str] = mapped_column(String(100), default="")
    temperature: Mapped[float] = mapped_column(Float, default=0.3)
    max_tokens: Mapped[int] = mapped_column(Integer, default=1024)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=False)
    scene_models: Mapped[dict] = mapped_column(JSON, default=dict)  # 场景模型分配
    proxy: Mapped[str] = mapped_column(String(255), default="")


class KnowledgePoint(Base):
    """知识点表：三级知识架构。"""

    __tablename__ = "knowledge_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    layer: Mapped[str] = mapped_column(String(20), default="basic")  # basic/tool/app
    category: Mapped[str] = mapped_column(String(50), default="")
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text, default="")
    example_code: Mapped[str] = mapped_column(Text, default="")
    difficulty: Mapped[str] = mapped_column(String(20), default="easy")
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    source: Mapped[str] = mapped_column(String(50), default="builtin")  # builtin/plugin


class Problem(Base):
    """题目表：编程训练场 / 作业。"""

    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    difficulty: Mapped[str] = mapped_column(String(20), default="easy")
    knowledge_point: Mapped[str] = mapped_column(String(100), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    example_input: Mapped[str] = mapped_column(Text, default="")
    example_output: Mapped[str] = mapped_column(Text, default="")
    test_cases: Mapped[list] = mapped_column(JSON, default=list)  # [{input, expected}]
    hints: Mapped[list] = mapped_column(JSON, default=list)  # [str]


class Submission(Base):
    """提交记录表：训练场 / 班级作业运行结果落库。"""

    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    problem_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    task_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 关联班级任务
    user_id: Mapped[int] = mapped_column(Integer, default=0)
    code: Mapped[str] = mapped_column(Text, default="")
    mode: Mapped[str] = mapped_column(String(20), default="track_a")  # track_a/track_b
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/success/failed
    score: Mapped[int] = mapped_column(Integer, default=0)
    run_time: Mapped[float] = mapped_column(Float, default=0.0)
    error_msg: Mapped[str] = mapped_column(Text, default="")
    ai_comment: Mapped[str] = mapped_column(Text, default="")
    passed: Mapped[bool] = mapped_column(Boolean, default=False)  # 测试用例是否通过
    similar_flag: Mapped[bool] = mapped_column(Boolean, default=False)  # 相似度预警
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否进入作品墙
    likes: Mapped[int] = mapped_column(Integer, default=0)  # 作品墙点赞数
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PeerReview(Base):
    """学生互评表：针对作品墙作品的评分与评语。"""

    __tablename__ = "peer_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    work_id: Mapped[int] = mapped_column(Integer, nullable=False)  # 关联 Submission.id
    reviewer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0)  # 1-5
    comment: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Class(Base):
    """班级表：教师创建，学生凭邀请码加入。"""

    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(Integer, nullable=False)
    class_name: Mapped[str] = mapped_column(String(120), nullable=False)
    major: Mapped[str] = mapped_column(String(80), default="")
    invite_code: Mapped[str] = mapped_column(String(6), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/archived
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ClassMember(Base):
    """班级成员关系：学生加入班级后写入。"""

    __tablename__ = "class_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="student")  # student
    group_name: Mapped[str] = mapped_column(String(50), default="")  # 分组
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Task(Base):
    """任务/作业表：支持三种出题方式，可关联班级。"""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 班级作业；空=公共题库
    creator_id: Mapped[int] = mapped_column(Integer, default=0)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Text] = mapped_column(Text, default="")
    knowledge_point: Mapped[str] = mapped_column(String(100), default="")
    difficulty: Mapped[str] = mapped_column(String(20), default="easy")
    test_cases: Mapped[list] = mapped_column(JSON, default=list)  # [{input, expected}]
    hints: Mapped[list] = mapped_column(JSON, default=list)
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    max_submissions: Mapped[int] = mapped_column(Integer, default=5)
    allow_ai: Mapped[bool] = mapped_column(Boolean, default=True)
    source: Mapped[str] = mapped_column(String(20), default="custom")  # bank/custom/ai
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LearningProgress(Base):
    """学习进度表：按知识点记录状态与正确率。"""

    __tablename__ = "learning_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    knowledge_point: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="未学")  # 未学/学习中/已掌握
    accuracy: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Checkin(Base):
    """学习打卡表：按用户每日去重。"""

    __tablename__ = "checkins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    checkin_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Badge(Base):
    """徽章表：规则枚举发放（连续打卡/满分作业/通关知识点）。"""

    __tablename__ = "badges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    badge_type: Mapped[str] = mapped_column(String(50), nullable=False)  # streak/full_score/mastery
    badge_name: Mapped[str] = mapped_column(String(120), default="")
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Plugin(Base):
    """插件登记表：记录已安装插件及启用状态（轻量市场）。"""

    __tablename__ = "plugins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), default="")
    version: Mapped[str] = mapped_column(String(20), default="0.1.0")
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(50), default="model")  # model/knowledge/eval
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
