<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { promptTrain } from '@/api/plans'
import { useUserStore } from '@/stores/user'
import { useAiConfigStore } from '@/stores/aiConfig'

const userStore = useUserStore()
const aiStore = useAiConfigStore()

const form = reactive({ requirement: '', prompt: '' })
const loading = ref(false)
const result = ref<{ generated_code: string; score: { clarity: number; boundary: number; correctness: number; efficiency: number; comment: string } } | null>(null)

async function run() {
  if (!form.requirement || !form.prompt) {
    ElMessage.warning('请填写业务需求与你编写的 Prompt')
    return
  }
  loading.value = true
  try {
    const params: any = { requirement: form.requirement, prompt: form.prompt }
    // 游客：复用本地 AI 配置；登录用户：服务端按云端配置调用
    if (!userStore.isLogin) {
      Object.assign(params, aiStore.buildChatParams())
    }
    result.value = await promptTrain(params)
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

const dims: { key: keyof NonNullable<typeof result.value>['score']; label: string }[] = [
  { key: 'clarity', label: 'Prompt 清晰度' },
  { key: 'boundary', label: '边界条件' },
  { key: 'correctness', label: '生成代码正确率' },
  { key: 'efficiency', label: '执行效率与规范' },
]
</script>

<template>
  <div class="py-container prompt-train">
    <h2 class="py-section-title">AI 协作编程 · Prompt 训练</h2>
    <p class="py-section-sub">
      模式 2（AI 编码面试模拟）：你不直接写代码，而是编写 Prompt 指令让 AI 生成代码。
      系统调用你配置的模型执行 Prompt，并从四个维度评分。
    </p>

    <div class="pt-grid">
      <div class="pt-left">
        <el-form label-position="top">
          <el-form-item label="业务需求">
            <el-input v-model="form.requirement" type="textarea" :rows="4" placeholder="例如：实现一个函数，输入学生分数列表，返回及格人数与平均分。" />
          </el-form-item>
          <el-form-item label="你编写的 Prompt">
            <el-input v-model="form.prompt" type="textarea" :rows="6" placeholder="例如：用 Python 写一个函数 count_pass(scores)，参数 scores 为数字列表，返回 (及格人数, 平均分)，保留两位小数。" />
          </el-form-item>
          <el-button type="primary" size="large" :loading="loading" @click="run">
            <el-icon><Cpu /></el-icon>&nbsp;运行评分
          </el-button>
          <p v-if="!userStore.isLogin" class="hint">未登录：将使用「AI 设置」中本地保存的 Key；登录后改由云端配置驱动。</p>
        </el-form>
      </div>

      <div class="pt-right" v-if="result">
        <div class="py-card score-card">
          <h4>评分</h4>
          <div v-for="d in dims" :key="d.key" class="score-row">
            <span class="score-name">{{ d.label }}</span>
            <el-progress :percentage="result.score[d.key]" :stroke-width="10" class="score-bar" />
          </div>
          <div class="comment"><b>评语：</b>{{ result.score.comment }}</div>
        </div>
        <div class="py-card code-card">
          <h4>模型生成的代码</h4>
          <pre class="gen-code">{{ result.generated_code }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.pt-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 22px; margin-top: 16px; }
.score-card, .code-card { padding: 18px 22px; margin-bottom: 16px; }
.score-card h4, .code-card h4 { margin: 0 0 14px; }
.score-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.score-name { width: 130px; font-size: 13px; }
.score-bar { flex: 1; }
.comment { font-size: 13px; line-height: 1.7; color: var(--text-main); }
.gen-code { background: #0f1b33; color: #e6edf7; padding: 14px; border-radius: 10px; font-size: 12.5px; white-space: pre-wrap; font-family: 'JetBrains Mono', Consolas, monospace; max-height: 360px; overflow: auto; }
.hint { font-size: 12px; color: var(--text-sub); margin-top: 10px; }
@media (max-width: 980px) { .pt-grid { grid-template-columns: 1fr; } }
</style>
