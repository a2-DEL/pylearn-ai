<div align="center">

# PyLearn AI

### 面向高校 Python 教学的开源双轨编程实训平台

**既练独立写代码，也练指挥 AI 写代码 —— 直接对接 2025 年企业 AI Coding 面试新题型**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![Vue 3](https://img.shields.io/badge/Vue-3.4-brightgreen.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)

</div>

---

## 为什么需要这个项目

大学 Python 课还在考手写递归，企业 2025 年以后的真实工作流已经变成：

> **人拆需求 → 写 Prompt → AI 出代码 → 人 Review/调试/合并**

市面上的 Python 学习产品：
- **纯文档**（菜鸟教程）—— 不能跑代码，看完就忘
- **算法刷题**（LeetCode）—— 全是两数之和，和业务脱节
- **录播课**（慕课网）—— 老师讲完就走，没有反馈闭环
- **付费数据课**（DataCamp）—— 英文、贵、不教 AI 协作

**没有一个产品专门训练"和 AI 一起写代码"这件新事。PyLearn AI 补的就是这块空白。**

---

## 核心能力

### 双轨编程训练（产品最锋利的差异）

| 轨道 | 模式 | 说明 |
|---|---|---|
| **轨道 A** 独立编程 | 写代码运行 | 传统基本功，自动跑测试用例批改，AI 解释报错 |
| **轨道 B** AI 协作 | ① 需求拆解训练 | 学生先写业务拆解，AI 对比标准方案点评 |
| | ② Prompt 编程训练 | 学生写 Prompt 让 AI 生成，四维评分 |
| | ③ 企业面试真题库 | 10 道真实业务题，隐藏测试用例跑 AI 输出 |
| | ④ 找 Bug 实战 | AI 埋雷学生排雷，测试全过才揭示答案 |
| | ⑤ 结对编程 | 学生写 TODO，AI 补全代码 |

### 班级教学（教师端开箱即用）
- 创建班级（自动 6 位邀请码）、学生批量导入、分组管理
- 三种出题方式：公共选题 / 自定义 / **AI 一键生成题目与测试用例**
- 自动批改：测试用例 + AI 代码评审（规范/可读/效率三维度）+ 相似度预警
- 学情看板：完成率、平均分、知识点热力图、学困生预警、**独立编程 vs AI 协作占比条**
- AI 教学方案：老师说"我是市场营销专业"，AI 出模块权重、分阶段计划、配套案例包
- 一键导出成绩 CSV

### 个人学习画像
- 学习统计：总提交 / 通过数 / 通过率 / 平均分
- **AI 协作依赖度仪表盘**：量化你有多少比例的提交是靠 AI 完成的，过高会提醒"先自己写再让 AI Review"
- 学习规划师：输入专业/水平/目标，AI 生成模块权重与阶段计划
- 最近提交历史（区分独立写 / AI 协作）

---

## 为什么选我们

| 维度 | LeetCode | DataCamp | PyLearn AI |
|---|---|---|---|
| 题目类型 | 纯算法 | 数据分析付费课 | 业务案例 + 算法 + AI 协作，全中文 |
| AI 协作训练 | ❌ | ❌ | ✅ 5 种模式 |
| 班级教学 | ❌ | 企业版才有 | ✅ 免费开源全功能 |
| 部署方式 | SaaS 闭源 | SaaS 闭源 | ✅ MIT 开源，可私有部署到内网 |
| 运行环境 | 只跑算法 | 自家浏览器 | ✅ 预装 pandas/numpy/matplotlib |
| 费用 | 会员制 | $25-33/月 | ✅ 软件免费，自备 API Key |

**别人做不到而我们能做到：**
- LeetCode 做不到：教市场营销学生做用户画像词云、自动批改班级作业、量化 AI 依赖度
- DataCamp 做不到：免费开源、中文、可内网部署、训练"写 Prompt 让 AI 写代码"
- 普通教程做不到：浏览器里直接跑 pandas 业务代码、配自己的 Key 用任意模型

---

## 核心竞争力（三句话）

1. **唯一同时训练"独立编程"与"AI 协作编程"双能力的开源平台** —— 直接对接 2025 年企业 AI Coding 面试新题型
2. **老师一句话生成专业教学方案** —— AI 按金融/营销/行政等专业背景定制模块权重、案例包与作业
3. **软件完全免费，用户自备算力** —— MIT 协议开源，API Key 自己管，可私有部署到学校内网，零平台成本

---

## 架构与工程亮点

- **统一 AI 网关插件化**：新增一个模型厂商只需 20 行适配器代码，兼容 DeepSeek / 豆包 / 通义千问 / 智谱 / OpenAI / Ollama
- **场景模型路由**：代码答疑、作业批改、案例生成可分别指定不同模型，省 token 成本
- **降级可用**：不配 AI Key 时整个系统退化为纯编程练习平台，内网/离线场景都能跑
- **预置教学库**：沙箱已装 numpy / pandas / matplotlib / seaborn / openpyxl / beautifulsoup4 / wordcloud，业务代码真能跑
- **Pydantic v2 + SQLAlchemy 2 异步**：FastAPI 自动生成 OpenAPI 文档，类型安全

### 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3.4 + TypeScript 5 + Vite 5 + Element Plus 2 + Monaco Editor + Pinia + ECharts |
| 后端 | Python 3.11+ / 3.13 验证可用 + FastAPI + SQLAlchemy 2 (async) + Pydantic v2 |
| 数据库 | 默认 SQLite（零配置），可切 PostgreSQL |
| AI 网关 | 统一抽象 + OpenAI 兼容适配器 + Mock 降级 |
| 沙箱 | 本地子进程，预装全量教学库 |

---

## 快速开始

### 后端

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env      # 按需修改
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

启动后访问 http://localhost:8000/docs 查看 Swagger 接口文档。

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173 。开发态 `/api` 已代理到后端 8000。

### 体验流程

1. 注册账号（密码至少 8 位，自己起用户名）
2. 右上角「AI 设置」：选 **Mock（无需 Key 即可体验）**，或填入 DeepSeek / 通义千问的 API Key
3. 「学习规划师」告诉 AI 你的专业与目标
4. 「编程训练场」写代码运行，报错点 AI 助手
5. 「面试真题库」写 Prompt 让 AI 写代码，看隐藏测试用例是否通过
6. 「找 Bug 训练」修 AI 埋的 bug，测试全过才给答案
7. 「班级中心」教师建班布置作业，学生凭邀请码加入
8. 「个人中心」看自己的 AI 协作依赖度

---

## 目录结构

```
PyLearn-AI/
├── backend/
│   ├── app/
│   │   ├── core/           # 配置 / 安全(AES) / DB / 限流
│   │   ├── models/         # ORM 模型
│   │   ├── routers/        # auth / classes / tasks / plans / sandbox / ai / ...
│   │   ├── services/
│   │   │   ├── sandbox/    # 代码沙箱
│   │   │   ├── ai/         # AI 网关 + debug_challenges / decompose / interview_questions
│   │   │   └── grading.py  # 自动批改
│   │   ├── templates/prompts/  # 提示词 YAML 模板
│   │   └── seed/           # 知识点与题目种子
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── views/          # Home / Practice / InterviewTrain / DebugTrain / LearnAdvisor / ...
│       ├── components/     # CodeEditor(Monaco) / AiAssistant
│       └── stores/ api/ utils/ router/
├── .env.example
└── README.md / LICENSE
```

---

## 配置说明

| 环境变量 | 说明 |
|---|---|
| `DATABASE_URL` | 默认 `sqlite+aiosqlite:///./pylearn.db`，可切 PostgreSQL |
| `REDIS_URL` | 留空自动回退内存限流 |
| `SANDBOX_BACKEND` | `local`（本地子进程，默认）或 `docker`（容器隔离，预留） |
| `AI_RATE_PER_MIN` / `AI_RATE_PER_DAY` | AI 限流 |
| `SECRET_KEY` / `AES_KEY` | 生产环境务必改为随机强值 |

---

## 安全说明

- API Key 全链路 AES 加密；前端回显仅显示后 4 位
- 个人 Key 默认存浏览器 localStorage，不上传服务器；云端同步需用户主动开启
- 沙箱运行在受限子进程，超时自动终止
- 日志不打印 API Key

---

## 路线图

- [x] MVP：沙箱运行 + AI 配置中心 + 基础训练场
- [x] 班级制：建班/作业/自动批改/学情看板
- [x] 双轨训练：5 种 AI 协作模式 + 企业面试真题库
- [x] AI 学习规划师 + 个人 AI 依赖度画像
- [ ] 真 Docker 容器沙箱（资源隔离升级）
- [ ] 案例包插件化（高校老师可贡献本专业案例）
- [ ] 自适应学习路径（根据错题自动跳知识点）

---

## 谁在用

- **高校 Python 公选课老师**：一个教案覆盖全专业的时代结束了
- **自学求职者**：在面试前练 AI Coding 新题型
- **学校机房/内网教学**：U 盘拷走就能用，不依赖外网
- **企业新员工培训**：按岗位方向定制案例包

---

## 参与贡献

欢迎提交 PR！请阅读 [CONTRIBUTING.md](./CONTRIBUTING.md)。

特别欢迎：
- 高校老师上传本专业案例包（医学统计、文本分析、用户画像……）
- 补充企业 AI Coding 面试真题
- 新增模型适配器

## License

[MIT](./LICENSE) © PyLearn AI Contributors
