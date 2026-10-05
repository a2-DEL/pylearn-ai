<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  listInterviewQuestions,
  submitInterview,
  type InterviewQuestion,
} from '@/api/plans'

const questions = ref<InterviewQuestion[]>([])
const activeId = ref(0)
const prompt = ref('')
const loading = ref(false)
const result = ref<Awaited<ReturnType<typeof submitInterview>> | null>(null)

onMounted(async () => {
  try {
    questions.value = await listInterviewQuestions()
    if (questions.value.length) select(questions.value[0])
  } catch {
    /* ignore */
  }
})

function select(q: InterviewQuestion) {
  activeId.value = q.id
  prompt.value = ''
  result.value = null
}

async function run() {
  if (!activeId.value) return
  if (!prompt.value.trim()) {
    ElMessage.warning('请先写下你给 AI 的指令（Prompt）')
    return
  }
  loading.value = true
  result.value = null
  try {
    result.value = await submitInterview(activeId.value, prompt.value)
    if (result.value.passed === result.value.total) ElMessage.success('全部用例通过！')
    else ElMessage.warning(`通过 ${result.value.passed}/${result.value.total} 个用例`)
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

const diffColor = (d: string) =>
  ({ easy: 'success', medium: 'warning', hard: 'danger' } as Record<string, string>)[d] || 'info'
</script>

<template>
  <div class="py-container interview">
    <h2 class="py-section-title">企业 AI Coding 面试模拟</h2>
    <p class="py-section-sub">
      真实面试新题型：你不写代码，而是写 Prompt 指挥 AI 生成。系统用隐藏测试用例跑 AI 的输出，
      从「Prompt 是否覆盖边界」和「代码是否正确」两个维度评分。
    </p>

    <div class="iv-grid">
      <aside class="iv-list py-card">
        <h4>真题库 <span class="cnt">{{ questions.length }} 题</span></h4>
        <div
          v-for="q in questions"
          :key="q.id"
          class="iv-item"
          :class="{ active: q.id === activeId }"
          @click="select(q)"
        >
          <div class="iv-item-title">{{ q.title }}</div>
          <div class="iv-item-meta">
            <el-tag :type="diffColor(q.difficulty)" size="small">{{ q.difficulty }}</el-tag>
            <span class="cat">{{ q.category }}</span>
          </div>
        </div>
      </aside>

      <section class="iv-main" v-if="questions.length">
        <div class="py-card qcard">
          <h3>{{ questions.find((q) => q.id === activeId)?.title }}</h3>
          <p class="req">{{ questions.find((q) => q.id === activeId)?.requirement }}</p>
          <label class="lbl">你写给 AI 的 Prompt：</label>
          <el-input
            v-model="prompt"
            type="textarea"
            :rows="5"
            placeholder="例如：用 Python 写一个 dedupe(lst) 函数，要求：1) 保持元素第一次出现的顺序；2) 不能直接用 set；3) 空列表返回空列表。"
          />
          <el-button type="primary" :loading="loading" class="run-btn" @click="run">
            <el-icon><VideoPlay /></el-icon>&nbsp;让 AI 写代码并评审
          </el-button>
        </div>

        <div class="py-card result" v-if="result">
          <div class="rh">
            <el-tag :type="result.passed === result.total ? 'success' : 'warning'" size="large">
              {{ result.passed === result.total ? '通过' : `${result.passed}/${result.total} 通过` }}
            </el-tag>
            <span class="score">综合得分 {{ result.score }}</span>
          </div>

          <h4>测试用例</h4>
          <div v-for="(c, i) in result.case_results" :key="i" class="cr-row" :class="c.passed ? 'ok' : 'bad'">
            <el-tag :type="c.passed ? 'success' : 'danger'" size="small">{{ c.passed ? 'PASS' : 'FAIL' }}</el-tag>
            <code>{{ c.call }}</code>
            <span class="exp">期望 {{ c.expected }}</span>
          </div>

          <h4>你的 Prompt 覆盖了哪些关键点</h4>
          <div class="kw">
            <el-tag v-for="k in result.hints_total" :key="k" :type="result.hints_hit.includes(k) ? 'success' : 'info'" class="kw-tag">
              {{ result.hints_hit.includes(k) ? '✓' : '·' }} {{ k }}
            </el-tag>
          </div>

          <p class="cmt" v-if="result.comment">{{ result.comment }}</p>

          <h4>AI 生成的代码</h4>
          <pre class="gen">{{ result.generated_code }}</pre>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped lang="scss">
.iv-grid { display: grid; grid-template-columns: 300px 1fr; gap: 22px; margin-top: 16px; }
.iv-list { padding: 16px; h4 { margin: 0 0 12px; display: flex; justify-content: space-between; } .cnt { color: var(--text-sub); font-weight: 400; font-size: 12px; } }
.iv-item { padding: 10px 12px; border-radius: 8px; cursor: pointer; margin-bottom: 6px; &:hover { background: var(--el-color-primary-light-9); } &.active { background: var(--el-color-primary-light-8); } }
.iv-item-title { font-size: 13px; margin-bottom: 6px; }
.iv-item-meta { display: flex; align-items: center; gap: 8px; .cat { font-size: 11px; color: var(--text-sub); } }
.iv-main { min-width: 0; }
.qcard { padding: 22px; margin-bottom: 16px; h3 { margin: 0 0 10px; } }
.req { line-height: 1.8; color: var(--text-main); background: var(--el-color-primary-light-9); padding: 12px 14px; border-radius: 10px; }
.lbl { display: block; font-size: 13px; color: var(--text-sub); margin: 14px 0 6px; }
.run-btn { margin-top: 12px; }
.result { padding: 22px; }
.rh { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
.score { font-size: 20px; font-weight: 700; color: var(--primary); }
h4 { margin: 16px 0 8px; font-size: 14px; }
.cr-row { display: flex; align-items: center; gap: 10px; padding: 6px 0; font-size: 13px; font-family: 'JetBrains Mono', Consolas, monospace; }
.cr-row code { background: #f1f4fa; padding: 2px 8px; border-radius: 4px; }
.cr-row.bad code { background: #fde8e8; }
.exp { color: var(--text-sub); font-size: 12px; }
.kw-tag { margin: 0 8px 8px 0; }
.cmt { margin-top: 10px; padding: 12px 14px; background: #fff7e6; border-left: 3px solid var(--warning); border-radius: 8px; line-height: 1.7; }
.gen { background: #0f1b33; color: #e6edf7; padding: 14px; border-radius: 10px; font-size: 12.5px; overflow: auto; line-height: 1.6; }
@media (max-width: 980px) { .iv-grid { grid-template-columns: 1fr; } }
</style>
