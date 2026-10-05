<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  listDebugChallenges,
  submitDebugFix,
  type DebugChallenge,
} from '@/api/plans'

const challenges = ref<DebugChallenge[]>([])
const activeId = ref<number>(0)
const code = ref('')
const loading = ref(false)
const result = ref<any>(null)

onMounted(async () => {
  try {
    challenges.value = await listDebugChallenges()
    if (challenges.value.length) select(challenges.value[0])
  } catch {
    /* ignore */
  }
})

function select(c: DebugChallenge) {
  activeId.value = c.id
  code.value = c.buggy_code
  result.value = null
}

async function run() {
  if (!activeId.value) return
  loading.value = true
  result.value = null
  try {
    result.value = await submitDebugFix(activeId.value, code.value)
    if (result.value.passed) ElMessage.success('全部测试通过，答案已揭示')
    else ElMessage.warning('还有测试未通过，继续排查')
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

const difficultyColor = (d: string) =>
  ({ easy: 'success', medium: 'warning', hard: 'danger' } as Record<string, string>)[d] || 'info'
</script>

<template>
  <div class="py-container debug-train">
    <h2 class="py-section-title">代码审查训练 · 找 Bug 模式</h2>
    <p class="py-section-sub">
      双轨 B 模式 3：AI 在代码里埋了 bug，你来做「排雷兵」。修改右侧代码直到测试用例全部通过，
      通过后才会展示参考答案——这正是企业 code review 岗的日常。
    </p>

    <div class="dt-grid">
      <aside class="dt-list py-card">
        <h4>训练题单</h4>
        <div
          v-for="c in challenges"
          :key="c.id"
          class="dt-item"
          :class="{ active: c.id === activeId }"
          @click="select(c)"
        >
          <div class="dt-item-title">#{{ c.id }} {{ c.title }}</div>
          <el-tag :type="difficultyColor(c.difficulty)" size="small">{{ c.difficulty }}</el-tag>
        </div>
      </aside>

      <section class="dt-main" v-if="challenges.length">
        <div class="py-card">
          <h3>{{ challenges.find((c) => c.id === activeId)?.title }}</h3>
          <p class="desc">{{ challenges.find((c) => c.id === activeId)?.description }}</p>
          <label class="code-label">你的修复（在埋雷版基础上改）：</label>
          <el-input
            v-model="code"
            type="textarea"
            :rows="12"
            class="code-editor"
            spellcheck="false"
          />
          <el-button type="primary" :loading="loading" class="run-btn" @click="run">
            <el-icon><VideoPlay /></el-icon>&nbsp;提交修复
          </el-button>
        </div>

        <div class="py-card result" v-if="result">
          <div class="result-head">
            <el-tag :type="result.passed ? 'success' : 'danger'" size="large">
              {{ result.passed ? '已通过' : '未通过' }}
            </el-tag>
            <span class="score">得分 {{ result.score }}</span>
          </div>

          <div class="cases">
            <div v-for="(t, i) in result.test_detail" :key="i" class="case-row" :class="{ bad: !t.passed }">
              <el-tag :type="t.passed ? 'success' : 'danger'" size="small">
                {{ t.passed ? 'PASS' : 'FAIL' }}
              </el-tag>
              <code>{{ t.input }}</code>
              <span v-if="t.result !== undefined" class="io">
                期望 {{ t.expected }} · 实际 {{ t.result }}
              </span>
              <span v-if="t.error" class="err">{{ t.error }}</span>
            </div>
          </div>

          <p class="comment">{{ result.comment }}</p>

          <div v-if="result.bugs_missed?.length" class="missed">
            <b>遗漏的 bug：</b>
            <ul><li v-for="(m, i) in result.bugs_missed" :key="i">{{ m }}</li></ul>
          </div>

          <div v-if="result.reference_revealed" class="ref">
            <h4>参考答案</h4>
            <pre>{{ result.reference_code }}</pre>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped lang="scss">
.dt-grid { display: grid; grid-template-columns: 280px 1fr; gap: 22px; margin-top: 16px; }
.dt-list { padding: 16px; h4 { margin: 0 0 12px; } }
.dt-item {
  padding: 10px 12px; border-radius: 8px; cursor: pointer; margin-bottom: 8px;
  display: flex; justify-content: space-between; align-items: center;
  &:hover { background: var(--el-color-primary-light-9); }
  &.active { background: var(--el-color-primary-light-8); }
}
.dt-item-title { font-size: 13px; }
.dt-main { min-width: 0; }
.desc { color: var(--text-sub); line-height: 1.7; margin: 8px 0 16px; }
.code-label { font-size: 13px; color: var(--text-sub); display: block; margin-bottom: 6px; }
:deep(.code-editor textarea) {
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 13px;
  background: #0f1b33;
  color: #e6edf7;
  line-height: 1.6;
}
.run-btn { margin-top: 12px; }
.result { margin-top: 16px; }
.result-head { display: flex; align-items: center; gap: 14px; margin-bottom: 12px; }
.score { font-size: 18px; font-weight: 600; color: var(--primary); }
.cases { margin: 8px 0 12px; }
.case-row { display: flex; align-items: center; gap: 10px; font-size: 13px; margin-bottom: 6px; flex-wrap: wrap; }
.case-row code { background: #f1f4fa; padding: 2px 6px; border-radius: 4px; }
.case-row.bad code { background: #fde8e8; }
.io { color: var(--text-sub); font-size: 12px; }
.err { color: #c0392b; font-size: 12px; }
.comment { line-height: 1.7; }
.missed { margin-top: 10px; color: #c0392b; }
.ref { margin-top: 14px; }
.ref pre {
  background: #0f1b33; color: #d4f7c5; padding: 14px; border-radius: 10px;
  font-size: 12.5px; overflow: auto;
}
@media (max-width: 980px) { .dt-grid { grid-template-columns: 1fr; } }
</style>
