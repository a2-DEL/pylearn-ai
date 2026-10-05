"""Pydantic v2 请求/响应模型。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# AI 配置
# --------------------------------------------------------------------------
class AIConfigCreate(BaseModel):
    provider: str = "auto"
    api_key: str = ""
    base_url: str = ""
    default_model: str = ""
    temperature: float = 0.3
    max_tokens: int = 1024
    is_synced: bool = False
    scene_models: Dict[str, str] = Field(default_factory=dict)
    proxy: str = ""


class AIConfigUpdate(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    default_model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_synced: Optional[bool] = None
    scene_models: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None


class AIConfigOut(BaseModel):
    id: int
    user_id: int
    provider: str
    api_key_masked: str
    base_url: str
    default_model: str
    temperature: float
    max_tokens: int
    is_synced: bool
    scene_models: Dict[str, str] = Field(default_factory=dict)
    proxy: str


class ConnectionTestResult(BaseModel):
    success: bool
    message: str
    models: List[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# 代码运行
# --------------------------------------------------------------------------
class RunCodeRequest(BaseModel):
    code: str
    problem_id: Optional[int] = None
    enable_network: bool = False
    language: str = "python"


class RunCodeResult(BaseModel):
    stdout: str = ""
    stderr: str = ""
    run_time: float = 0.0
    success: bool = False
    error: str = ""


# --------------------------------------------------------------------------
# 题目 / 知识点
# --------------------------------------------------------------------------
class ProblemCreate(BaseModel):
    title: str
    difficulty: str = "easy"
    knowledge_point: str = ""
    description: str = ""
    example_input: str = ""
    example_output: str = ""
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)


class ProblemOut(BaseModel):
    id: int
    title: str
    difficulty: str
    knowledge_point: str
    description: str
    example_input: str
    example_output: str
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)


class KnowledgePointOut(BaseModel):
    id: int
    layer: str
    category: str
    slug: str
    title: str
    content: str
    example_code: str
    difficulty: str
    order_index: int
    source: str = "builtin"


# --------------------------------------------------------------------------
# 提交
# --------------------------------------------------------------------------
class SubmissionOut(BaseModel):
    id: int
    problem_id: Optional[int]
    user_id: int
    code: str
    status: str
    score: int
    run_time: float
    error_msg: str
    ai_comment: str
    passed: bool = False
    is_public: bool = True
    likes: int = 0
    submitted_at: Any = None


# --------------------------------------------------------------------------
# AI 对话 / 答疑
# --------------------------------------------------------------------------
class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    provider: Optional[str] = None
    api_key: Optional[str] = None  # 游客：前端传明文，服务端不落库
    base_url: Optional[str] = None
    model: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 1024
    stream: bool = False


class ExplainRequest(BaseModel):
    code: str
    error_msg: Optional[str] = None
    question: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


# --------------------------------------------------------------------------
# 认证与权限
# --------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: Optional[str] = None
    password: str = Field(min_length=8, max_length=128)
    roles: str = "student"  # student / teacher，可逗号组合


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    roles: str


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    roles: str
    created_at: Any = None
    last_login: Any = None


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=128)


# --------------------------------------------------------------------------
# 班级
# --------------------------------------------------------------------------
class ClassCreate(BaseModel):
    class_name: str = Field(min_length=1, max_length=120)
    major: str = ""
    description: str = ""


class ClassUpdate(BaseModel):
    class_name: Optional[str] = None
    major: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class ClassOut(BaseModel):
    id: int
    teacher_id: int
    class_name: str
    major: str
    invite_code: str
    description: str
    status: str
    created_at: Any = None
    student_count: int = 0


class JoinClassRequest(BaseModel):
    invite_code: str


class MemberOut(BaseModel):
    user_id: int
    username: str
    role: str = "student"
    group_name: str = ""
    joined_at: Any = None


# --------------------------------------------------------------------------
# 任务 / 作业
# --------------------------------------------------------------------------
class TaskCreate(BaseModel):
    class_id: Optional[int] = None
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    knowledge_point: str = ""
    difficulty: str = "easy"
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)
    deadline: Optional[Any] = None
    max_submissions: int = 5
    allow_ai: bool = True
    source: str = "custom"


class TaskOut(BaseModel):
    id: int
    class_id: Optional[int] = None
    creator_id: int
    title: str
    description: str
    knowledge_point: str
    difficulty: str
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)
    deadline: Any = None
    max_submissions: int
    allow_ai: bool
    source: str
    created_at: Any = None


class SubmitRequest(BaseModel):
    code: str
    mode: str = "track_a"  # track_a 独立 / track_b AI协作
    prompt: Optional[str] = None  # 轨道B：学生编写的 Prompt


class GradingResult(BaseModel):
    status: str  # success/failed
    passed: bool
    score: int
    run_time: float
    error_msg: str = ""
    ai_comment: str = ""
    test_detail: List[Dict[str, Any]] = Field(default_factory=list)
    similar_flag: bool = False


# --------------------------------------------------------------------------
# 学习进度
# --------------------------------------------------------------------------
class ProgressUpsert(BaseModel):
    knowledge_point: str
    status: str = "学习中"  # 未学/学习中/已掌握
    accuracy: float = 0.0


class ProgressOut(BaseModel):
    id: int
    user_id: int
    knowledge_point: str
    status: str
    accuracy: float
    updated_at: Any = None


# --------------------------------------------------------------------------
# 教学方案 / Prompt 训练评分
# --------------------------------------------------------------------------
class TeachingPlanRequest(BaseModel):
    major: str
    goal: str = ""
    style: str = ""


class PromptTrainRequest(BaseModel):
    requirement: str
    prompt: str
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


# --------------------------------------------------------------------------
# 阶段三：AI 陪练 / 学习路径 / 错题本
# --------------------------------------------------------------------------
class ReviewRequest(BaseModel):
    code: str
    language: str = "python"
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


class ReviewResult(BaseModel):
    comments: str = ""          # 评审与重构建议（Markdown）
    complexity: str = ""        # 复杂度评估
    risks: List[str] = Field(default_factory=list)
    score: int = 0              # 代码质量分 0-100


class TutorRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = Field(default_factory=list)  # [{role, content}]
    knowledge_point: Optional[str] = None
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None


class MistakeOut(BaseModel):
    submission_id: int
    problem_id: Optional[int]
    task_id: Optional[int]
    knowledge_point: str = ""
    code: str
    error_msg: str
    ai_comment: str
    score: int
    mode: str = "track_a"
    submitted_at: Any = None


class LearningPathOut(BaseModel):
    user_id: int
    recommended: List[Dict[str, Any]] = Field(default_factory=list)  # 推荐知识点序列
    weak_points: List[str] = Field(default_factory=list)            # 薄弱知识点


# --------------------------------------------------------------------------
# 阶段三：竞赛 / 排行 / 作品墙 / 互评
# --------------------------------------------------------------------------
class RankEntry(BaseModel):
    user_id: int
    username: str
    total_score: int = 0
    passed_count: int = 0
    submission_count: int = 0
    avg_score: float = 0.0


class RankOut(BaseModel):
    scope: str = "class"        # class/school
    class_id: Optional[int] = None
    entries: List[RankEntry] = Field(default_factory=list)


class WorkOut(BaseModel):
    id: int
    user_id: int
    username: str
    problem_id: Optional[int]
    problem_title: str = ""
    task_id: Optional[int]
    code: str
    score: int
    run_time: float
    submitted_at: Any = None
    likes: int = 0


class WorkLikeResponse(BaseModel):
    likes: int


class PeerReviewCreate(BaseModel):
    work_id: int
    score: int = Field(ge=1, le=5)
    comment: str = ""


class PeerReviewOut(BaseModel):
    id: int
    work_id: int
    reviewer_id: int
    reviewer_name: str = ""
    score: int
    comment: str
    created_at: Any = None


# --------------------------------------------------------------------------
# 阶段三：打卡 / 徽章
# --------------------------------------------------------------------------
class CheckinOut(BaseModel):
    date: str
    streak: int = 0             # 当前连续天数
    total: int = 0


class BadgeOut(BaseModel):
    id: int
    user_id: int
    badge_type: str
    badge_name: str
    reason: str
    created_at: Any = None


# --------------------------------------------------------------------------
# 阶段三：插件市场
# --------------------------------------------------------------------------
class PluginOut(BaseModel):
    name: str
    display_name: str
    version: str
    description: str
    category: str
    enabled: bool
    config: Dict[str, Any] = Field(default_factory=dict)


class PluginUpdate(BaseModel):
    enabled: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
