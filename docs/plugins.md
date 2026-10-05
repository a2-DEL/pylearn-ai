# 插件开发文档

PyLearn AI 采用插件化架构，核心能力通过抽象层解耦，新增能力通常**无需修改核心代码**。

## 一、新增 AI 模型适配器

所有模型适配器实现 `app/services/ai/base.py` 的 `BaseAIGateway`：

```python
class BaseAIGateway(ABC):
    async def chat(self, messages, temperature=0.3, max_tokens=1024) -> str: ...
    async def stream_chat(self, messages, temperature=0.3, max_tokens=1024) -> AsyncGenerator[str, None]: ...
    async def check_connection(self) -> tuple[bool, str]: ...
    async def list_models(self) -> List[str]: ...
```

### 情形 A：OpenAI 兼容协议（最常见）

DeepSeek / 字节豆包 / 通义千问 / 智谱清言 / Ollama 等均兼容 OpenAI 格式。
只需在 `app/services/ai/detector.py` 的 `DEFAULT_BASE_URLS` / `DEFAULT_MODELS` 增加厂商条目，
并在 `factory.build_gateway` 中登记 `provider` 即可，**无需新写类**。

```python
DEFAULT_BASE_URLS["myai"] = "https://api.myai.com/v1"
DEFAULT_MODELS["myai"] = "myai-default"
```

### 情形 B：非兼容协议（如 Claude / Gemini）

新建 `app/services/ai/myai.py`，继承 `BaseAIGateway`，自行处理消息格式转换、参数映射与响应解析，
并在 `factory.build_gateway` 中按 `provider` 返回你的适配器实例。

## 二、自动识别厂商

`detector.auto_detect(base_url, api_key)` 先按 `DEFAULT_BASE_URLS` 的域名前缀匹配，
再调用 `/v1/models` 探测模型列表。新增厂商时补充 `PROVIDER_DOMAINS` 即可被自动识别。

## 三、提示词模板

业务提示词放在 `app/templates/prompts/`，按场景一个 YAML 文件：

```yaml
name: my_scene
system: |
  你是 ...（角色设定）
user: |
  学生代码：
  ```python
  {{code}}
  ```
```

通过 `app/services/ai/prompts.py` 的 `build_messages("my_scene", code=...)` 渲染，
模板变量使用 `{{var}}` 注入。新增场景复制一个 YAML 即可。

## 四、新增代码沙箱实现

实现 `app/services/ai/sandbox/base.py` 的 `SandboxBase.run(code, timeout, enable_network)`，
返回 `{stdout, stderr, run_time, success, error}`，并在 `factory.get_sandbox()` 中登记，
通过环境变量 `SANDBOX_BACKEND` 切换。当前 `LocalSandbox` 为兜底，`DockerSandbox` 为容器占位。

## 五、新增知识点 / 习题

- 知识点：在 `app/seed/data.py` 的 `KNOLEDGE_POINTS` 增加条目（幂等写入，重启自动入库）
- 习题：在 `PROBLEMS` 增加，字段含 `title / difficulty / knowledge_point / description /
  example_input / example_output / test_cases / hints`

> 后续将提供文件化插件目录（如 `plugins/problems/*.yaml`）实现免改代码扩展，敬请期待。
