# 贡献指南 (CONTRIBUTING)

感谢参与 PyLearn AI 开源建设！本指南帮助你快速上手开发规范。

## 开发流程

1. Fork 本仓库并拉取最新 `main`
2. 创建特性分支：`git checkout -b feat/your-feature`
3. 本地按 README 启动前后端
4. 提交前确保：后端 `python -m py_compile` 通过、前端 `npm run build` 通过
5. 提交 PR，描述变更点与验收方式

## 代码规范

### 后端（Python）

- 遵循 PEP 8；类型注解完整（FastAPI / Pydantic v2 强依赖）
- 业务接口只依赖抽象层：代码执行依赖 `SandboxBase`，AI 调用依赖 `BaseAIGateway`
- 新增接口返回统一结构 `{code, message, data}`（异常由 `core/exceptions.py` 处理）
- 不硬编码配置，统一使用 `core/config.py` 的 Settings（环境变量覆盖）
- API Key 等敏感信息必须加密，禁止写入日志

### 前端（Vue 3 + TS）

- `<script setup>` + Composition API；组件语义化命名，公共组件放入 `components/`
- 接口请求集中到 `api/`；状态放 `stores/`（Pinia）
- 样式使用 SCSS，遵循 `styles/main.scss` 的主题变量
- 提交前运行 `npm run build`（含 `vue-tsc` 类型检查）

## 提交信息

推荐格式：`feat:` / `fix:` / `docs:` / `refactor:` / `chore:` + 简述。

## 行为准则

- 友好、开放、就事论事
- 不提交任何密钥、个人信息或违规内容

## 插件化扩展

平台采用插件化架构，新增能力无需改动核心代码：

### 新增 AI 模型适配器

1. 若模型兼容 OpenAI 协议：直接在 `backend/app/services/ai/detector.py` 的 `_PROVIDER_DOMAINS` / `DEFAULT_BASE_URLS` / `DEFAULT_MODELS` 增加厂商映射即可，无需新类
2. 非兼容模型：在 `backend/app/services/ai/` 下新建适配器类继承 `BaseAIGateway`，实现 `chat` / `stream_chat` / `check_connection` / `list_models`，并在 `factory.py` 注册
3. 提示词模板置于 `backend/app/templates/prompts/*.yaml`，使用 `{{var}}` 注入，调用 `services/ai/prompts.py` 的 `build_messages`

### 新增知识点 / 案例 / 题目

- 直接写入 `backend/app/seed/data.py` 的 `KNOWLEDGE_POINTS` / `PROBLEMS`（幂等种子），或经接口 `POST /api/knowledge`、`POST /api/problems`、`POST /api/tasks` 入库
- 前端案例库在 `frontend/src/views/Cases.vue` 的 `cases` 数组维护

### 切换代码沙箱

- 本地兜底：`SANDBOX_BACKEND=local`（默认，无 Docker 可用）
- 容器沙箱：实现 `backend/app/services/sandbox/docker.py` 的 `DockerSandbox`（已预留接口），设 `SANDBOX_BACKEND=docker`

