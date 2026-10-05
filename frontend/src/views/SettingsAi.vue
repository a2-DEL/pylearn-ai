<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAiConfigStore } from '@/stores/aiConfig'
import { testConnection, createAiConfig } from '@/api/aiConfig'
import { detectConfig } from '@/api/ai'
import { maskApiKey } from '@/utils/crypto'
import { useUserStore } from '@/stores/user'

const store = useAiConfigStore()
const userStore = useUserStore()
const cfg = store.config

const providers = [
  { value: 'auto', label: '自动识别' },
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'doubao', label: '字节豆包' },
  { value: 'qwen', label: '通义千问' },
  { value: 'zhipu', label: '智谱清言' },
  { value: 'openai', label: 'OpenAI' },
  { value: 'ollama', label: 'Ollama（本地）' },
  { value: 'custom', label: '自定义' },
  { value: 'mock', label: 'Mock（无需 Key 演示）' },
]

const testing = ref(false)
const connResult = ref<{ success: boolean; message: string } | null>(null)
const detecting = ref(false)
const modelOptions = ref<string[]>([])

const maskedPreview = computed(() => (cfg.api_key ? maskApiKey(cfg.api_key) : '未填写'))

async function onTest() {
  testing.value = true
  connResult.value = null
  try {
    const res = await testConnection({
      provider: cfg.provider,
      api_key: cfg.api_key,
      base_url: cfg.base_url,
      default_model: cfg.default_model,
      proxy: cfg.proxy,
    })
    connResult.value = { success: res.success, message: res.message }
    if (res.success && res.models.length) {
      modelOptions.value = res.models
      if (!cfg.default_model) cfg.default_model = res.models[0]
    }
  } catch {
    /* 拦截器已提示 */
  } finally {
    testing.value = false
  }
}

async function onDetect() {
  if (!cfg.base_url && !cfg.api_key) {
    ElMessage.warning('请先填写 Base URL 或 API Key')
    return
  }
  detecting.value = true
  try {
    const res = await detectConfig({ base_url: cfg.base_url, api_key: cfg.api_key })
    cfg.provider = res.provider === 'custom' ? 'custom' : res.provider
    if (res.base_url) cfg.base_url = res.base_url
    if (res.models.length) {
      modelOptions.value = res.models
      cfg.default_model = res.default_model
    }
    ElMessage.success(`识别为厂商：${res.provider}`)
  } catch {
    /* ignore */
  } finally {
    detecting.value = false
  }
}

async function onSave() {
  store.save()
  if (cfg.is_synced && userStore.isLogin) {
    try {
      await createAiConfig({
        provider: cfg.provider,
        api_key: cfg.api_key,
        base_url: cfg.base_url,
        default_model: cfg.default_model,
        temperature: cfg.temperature,
        max_tokens: cfg.max_tokens,
        is_synced: true,
        scene_models: cfg.scene_models,
        proxy: cfg.proxy,
      })
      ElMessage.success('已本地保存并加密同步至云端')
    } catch {
      ElMessage.warning('本地已保存，但云端同步失败（请确认已登录）')
    }
  } else {
    ElMessage.success('已保存到本地（AES 加密）')
  }
}

function onReset() {
  store.reset()
  modelOptions.value = []
  connResult.value = null
  ElMessage.info('已恢复默认配置')
}
</script>

<template>
  <div class="py-container settings">
    <h2 class="py-section-title">AI 配置中心</h2>
    <p class="py-section-sub">
      自备算力：模型由你自己的 API Key 驱动，平台零 API 成本。配置默认加密存于浏览器本地。
    </p>

    <div class="py-card basic">
      <div class="block-title">基础配置</div>

      <el-alert
        v-if="connResult"
        :type="connResult.success ? 'success' : 'error'"
        :closable="false"
        show-icon
        class="conn-alert"
      >
        {{ connResult.message }}
      </el-alert>

      <el-form label-width="120px" class="form">
        <el-form-item label="模型厂商">
          <el-select v-model="cfg.provider" placeholder="选择厂商" style="width: 320px">
            <el-option v-for="p in providers" :key="p.value" :label="p.label" :value="p.value" />
          </el-select>
        </el-form-item>

        <el-form-item label="API Key">
          <el-input
            v-model="cfg.api_key"
            type="password"
            show-password
            placeholder="sk-...（输入后仅本地加密保存）"
            style="width: 460px"
          />
          <span class="mask-preview">回显：{{ maskedPreview }}</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="testing" @click="onTest">
            <el-icon><Connection /></el-icon>&nbsp;测试连接
          </el-button>
          <el-button :loading="detecting" @click="onDetect">
            <el-icon><MagicStick /></el-icon>&nbsp;自动识别
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-collapse class="adv">
      <el-collapse-item title="高级配置" name="1">
        <div class="py-card adv-body">
          <el-form label-width="120px" class="form">
            <el-form-item label="Base URL">
              <el-input
                v-model="cfg.base_url"
                placeholder="自定义接口地址（兼容本地/代理/中转）"
                style="width: 460px"
              />
            </el-form-item>

            <el-form-item label="默认模型">
              <el-select
                v-model="cfg.default_model"
                filterable
                allow-create
                placeholder="选择或输入模型名"
                style="width: 320px"
              >
                <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
              </el-select>
            </el-form-item>

            <el-form-item label="温度 (temperature)">
              <el-slider v-model="cfg.temperature" :min="0" :max="2" :step="0.1" style="width: 360px" />
              <span class="slider-val">{{ cfg.temperature }}</span>
            </el-form-item>

            <el-form-item label="最大输出 Token">
              <el-input-number v-model="cfg.max_tokens" :min="256" :max="8192" :step="256" />
            </el-form-item>

            <el-form-item label="代理设置">
              <el-input
                v-model="cfg.proxy"
                placeholder="http:// 或 https:// 代理地址（可选）"
                style="width: 460px"
              />
            </el-form-item>

            <el-form-item label="云端同步">
              <el-switch v-model="cfg.is_synced" />
              <span class="hint-text">（默认关闭，开启后将加密同步至服务端）</span>
            </el-form-item>
          </el-form>

          <div class="adv-actions">
            <el-button type="danger" plain @click="onReset">
              <el-icon><RefreshLeft /></el-icon>&nbsp;恢复默认
            </el-button>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>

    <div class="save-bar">
      <el-button type="primary" size="large" @click="onSave">保存配置</el-button>
      <span class="hint-text">保存后立即在训练场可用（无需刷新页面）</span>
    </div>
  </div>
</template>

<style scoped lang="scss">
.basic {
  padding: 22px 24px;
  margin-bottom: 16px;
}
.block-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--primary);
}
.conn-alert {
  margin-bottom: 16px;
}
.form {
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }
}
.mask-preview {
  margin-left: 14px;
  font-size: 12px;
  color: var(--text-sub);
  font-family: monospace;
}
.slider-val {
  margin-left: 14px;
  font-size: 13px;
  color: var(--primary);
  font-weight: 600;
}
.adv {
  :deep(.el-collapse-item__header) {
    font-weight: 600;
    font-size: 15px;
    color: var(--primary);
  }
}
.adv-body {
  padding: 20px 22px;
}
.adv-actions {
  margin-top: 10px;
}
.hint-text {
  font-size: 12px;
  color: var(--text-sub);
  margin-left: 12px;
}
.save-bar {
  margin: 22px 0 40px;
  display: flex;
  align-items: center;
  gap: 14px;
}
</style>
