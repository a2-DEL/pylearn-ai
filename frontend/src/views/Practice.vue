<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { listProblems, getProblem, type Problem } from '@/api/problems'
import { runCode, type RunResult } from '@/api/sandbox'
import { getTask, submitTask, type TaskOut, type GradingResult } from '@/api/tasks'
import CodeEditor from '@/components/CodeEditor.vue'
import AiAssistant from '@/components/AiAssistant.vue'

const route = useRoute()
const problems = ref<Problem[]>([])
const active = ref<Problem | null>(null)
const code = ref('# 在此编写你的解答\n')
const running = ref(false)
const result = ref<RunResult | null>(null)
const hintsShown = ref(0)
const bottomOpen = ref(true)
const activeTab = ref<'output' | 'ai'>('output')

// 班级任务模式
const isTask = ref(false)
const taskId = ref<number | null>(null)
const grade = ref<GradingResult | null>(null)

const aiRef = ref<InstanceType<typeof AiAssistant> | null>(null)

const splitPct = ref(45)
const containerRef = ref<HTMLElement | null>(null)
let dragging = false

const difficultyType: Record<string, 'success' | 'warning' | 'danger'> = {
  easy: 'success',
  medium: 'warning',
  hard: 'danger',
}

function difficultyText(d: string) {
  return d === 'easy' ? '简单' : d === 'medium' ? '中等' : '较难'
}

async function selectProblem(p: Problem) {
  const full = await getProblem(p.id)
  active.value = full
  code.value = '# 在此编写你的解答\n'
  hintsShown.value = 0
  result.value = null
  grade.value = null
  isTask.value = false
  taskId.value = null
  activeTab.value = 'output'
}

function showNextHint() {
  if (active.value && hintsShown.value < active.value.hints.length) hintsShown.value++
}

async function run() {
  if (!active.value) return
  running.value = true
  activeTab.value = 'output'
  try {
    if (isTask.value && taskId.value) {
      // 班级任务：提交并自动批改（测试用例 + AI 评审）
      grade.value = await submitTask(taskId.value, { code: code.value, mode: 'track_a' })
      result.value = null
    } else {
      result.value = await runCode({ code: code.value, problem_id: active.value.id })
      grade.value = null
      if (!result.value.success) aiRef.value?.askExplain()
    }
  } catch {
    /* 错误已在拦截器提示 */
  } finally {
    running.value = false
  }
}

function resetCode() {
  code.value = '# 在此编写你的解答\n'
  ElMessage.info('已重置代码')
}

// 拖拽分隔
function startDrag() {
  dragging = true
  document.addEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  window.addEventListener('mouseup', stopDrag)
}
function onDrag(e: MouseEvent) {
  if (!dragging || !containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  const pct = ((e.clientX - rect.left) / rect.width) * 100
  splitPct.value = Math.min(70, Math.max(28, pct))
}
function stopDrag() {
  dragging = false
  document.removeEventListener('mousemove', onDrag)
  window.removeEventListener('mouseup', stopDrag)
}

onMounted(async () => {
  problems.value = await listProblems()
  const tid = route.query.task ? Number(route.query.task) : 0
  if (tid) {
    try {
      const t: TaskOut = await getTask(tid)
      isTask.value = true
      taskId.value = t.id
      active.value = {
        id: t.id,
        title: t.title,
        difficulty: t.difficulty,
        knowledge_point: t.knowledge_point,
        description: t.description,
        example_input: '',
        example_output: '',
        test_cases: t.test_cases,
        hints: t.hints,
      } as unknown as Problem
      code.value = '# 在此编写你的解答\n'
      hintsShown.value = 0
      grade.value = null
      return
    } catch {
      /* 回退到普通题库 */
    }
  }
  if (problems.value.length) await selectProblem(problems.value[0])
})
</script>

<template>
  <div class="practice">
    <div class="practice-head">
      <div class="py-container head-inner">
        <el-select
          v-model="active"
          value-key="id"
          placeholder="选择题目"
          size="large"
          class="prob-select"
          @change="selectProblem"
        >
          <el-option v-for="p in problems" :key="p.id" :value="p" :label="p.title" />
        </el-select>
        <div v-if="active" class="head-tags">
          <el-tag :type="difficultyType[active.difficulty]">{{ difficultyText(active.difficulty) }}</el-tag>
          <el-tag type="info" v-if="active.knowledge_point">{{ active.knowledge_point }}</el-tag>
        </div>
      </div>
    </div>

    <div class="py-container main-wrap">
      <div class="split" ref="containerRef">
        <section class="pane left" :style="{ width: splitPct + '%' }">
          <div class="pane-scroll">
            <h2 v-if="active" class="prob-title">{{ active.title }}</h2>
            <div v-if="active" class="prob-desc">{{ active.description }}</div>

            <template v-if="active">
              <h4 class="mini">示例输入</h4>
              <pre class="code-block">{{ active.example_input }}</pre>
              <h4 class="mini">示例输出</h4>
              <pre class="code-block">{{ active.example_output }}</pre>

              <div class="hints">
                <el-button :disabled="!active.hints.length" @click="showNextHint">
                  <el-icon><Promotion /></el-icon>&nbsp;获取提示 ({{ hintsShown }}/{{ active.hints.length }})
                </el-button>
                <div v-for="(h, i) in active.hints.slice(0, hintsShown)" :key="i" class="hint-item">
                  <b>提示 {{ i + 1 }}：</b>{{ h }}
                </div>
              </div>
            </template>
          </div>
        </section>

        <div class="divider" @mousedown="startDrag"></div>

        <section class="pane right">
          <div class="editor-bar">
            <span class="lang">Python 3.11</span>
            <div class="editor-actions">
              <el-button @click="resetCode">
                <el-icon><RefreshLeft /></el-icon>&nbsp;重置
              </el-button>
              <el-button type="primary" :loading="running" @click="run">
                <el-icon><VideoPlay /></el-icon>&nbsp;{{ running ? '运行中…' : (isTask ? '提交并批改' : '运行') }}
              </el-button>
            </div>
          </div>
          <div class="editor-host">
            <CodeEditor v-model="code" language="python" />
          </div>
        </section>
      </div>

      <div class="bottom" :class="{ collapsed: !bottomOpen }">
        <div class="bottom-head" @click="bottomOpen = !bottomOpen">
          <span>控制台</span>
          <el-icon class="caret" :class="{ up: bottomOpen }"><ArrowUp /></el-icon>
        </div>
        <div class="bottom-body" v-show="bottomOpen">
          <el-tabs v-model="activeTab" class="bottom-tabs">
            <el-tab-pane label="运行结果" name="output">
              <div v-if="!result && !grade" class="placeholder">点击「运行」查看输出</div>
              <div v-if="grade" class="result">
                <div class="result-meta">
                  <el-tag :type="grade.passed ? 'success' : 'danger'">
                    {{ grade.passed ? '通过' : '未通过' }}
                  </el-tag>
                  <span>得分 {{ grade.score }}</span>
                  <span>耗时 {{ grade.run_time }}s</span>
                  <el-tag v-if="grade.similar_flag" type="warning" size="small">相似度预警</el-tag>
                </div>
                <pre v-if="grade.error_msg" class="out stderr">{{ grade.error_msg }}</pre>
                <div class="test-detail" v-if="grade.test_detail.length">
                  <div v-for="(t, i) in grade.test_detail" :key="i" class="td-row" :class="t.passed ? 'ok' : 'fail'">
                    <span>用例 {{ i + 1 }}</span>
                    <span>{{ t.passed ? '通过' : '未通过' }}</span>
                    <span v-if="t.error" class="td-err">{{ t.error }}</span>
                    <span v-else>结果：{{ t.result }}</span>
                  </div>
                </div>
                <div class="ai-comment" v-if="grade.ai_comment">
                  <b>AI 评语：</b>{{ grade.ai_comment }}
                </div>
              </div>
              <div v-else-if="result" class="result">
                <div class="result-meta">
                  <el-tag :type="result.success ? 'success' : 'danger'">
                    {{ result.success ? '执行成功' : '执行失败' }}
                  </el-tag>
                  <span>耗时 {{ result.run_time }}s</span>
                </div>
                <pre v-if="result.stdout" class="out stdout">{{ result.stdout }}</pre>
                <pre v-if="result.stderr" class="out stderr">{{ result.stderr || result.error }}</pre>
                <pre v-if="!result.stdout && !result.stderr" class="out">{{ result.error || '（无输出）' }}</pre>
              </div>
            </el-tab-pane>
            <el-tab-pane label="AI 助手" name="ai">
              <AiAssistant ref="aiRef" :code="code" :error-msg="result?.error || result?.stderr" />
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.practice {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px - 60px);
}
.practice-head {
  background: #fff;
  border-bottom: 1px solid rgba(31, 42, 61, 0.08);
}
.head-inner {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 60px;
}
.prob-select {
  width: 280px;
}
.head-tags {
  display: flex;
  gap: 8px;
}
.main-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding-top: 16px;
  padding-bottom: 16px;
  min-height: 0;
}
.split {
  flex: 1;
  display: flex;
  min-height: 0;
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: var(--shadow-card);
}
.pane {
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.pane-scroll {
  overflow-y: auto;
  padding: 20px 22px;
}
.prob-title {
  margin: 0 0 12px;
  font-size: 20px;
}
.prob-desc {
  line-height: 1.8;
  color: var(--text-main);
  white-space: pre-wrap;
}
.mini {
  margin: 18px 0 6px;
  font-size: 13px;
  color: var(--text-sub);
}
.code-block {
  background: #0f1b33;
  color: #e6edf7;
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 12.5px;
  margin: 0;
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', Consolas, monospace;
}
.hints {
  margin-top: 18px;
}
.hint-item {
  margin-top: 10px;
  padding: 12px 14px;
  background: var(--el-color-primary-light-9);
  border-left: 3px solid var(--primary);
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.7;
}
.divider {
  width: 6px;
  cursor: col-resize;
  background: rgba(31, 42, 61, 0.06);
  transition: background 0.2s;
}
.divider:hover {
  background: var(--primary);
}
.right {
  flex: 1;
  min-width: 0;
}
.editor-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(31, 42, 61, 0.08);
}
.lang {
  font-size: 12px;
  color: var(--text-sub);
}
.editor-actions {
  display: flex;
  gap: 8px;
}
.editor-host {
  flex: 1;
  min-height: 0;
}
.bottom {
  margin-top: 14px;
  background: #fff;
  border-radius: 14px;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.bottom-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 18px;
  cursor: pointer;
  font-weight: 600;
  border-bottom: 1px solid rgba(31, 42, 61, 0.06);
}
.caret {
  transition: transform 0.2s;
}
.caret.up {
  transform: rotate(180deg);
}
.bottom-body {
  height: 260px;
}
.bottom-tabs {
  height: 100%;
  :deep(.el-tabs__header) {
    margin: 0;
    padding: 0 14px;
  }
  :deep(.el-tabs__content) {
    height: calc(100% - 40px);
    overflow: hidden;
  }
  :deep(.el-tab-pane) {
    height: 100%;
  }
}
.placeholder {
  padding: 30px;
  color: var(--text-sub);
  text-align: center;
}
.result {
  padding: 14px 18px;
  overflow-y: auto;
  height: 100%;
}
.result-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  span {
    font-size: 12px;
    color: var(--text-sub);
  }
}
.out {
  padding: 12px 14px;
  border-radius: 10px;
  font-size: 13px;
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', Consolas, monospace;
  margin: 0 0 10px;
}
.stdout {
  background: #f3f8f3;
  color: #1f2a3d;
}
.stderr {
  background: #fdeced;
  color: #b42318;
}
.test-detail {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}
.td-row {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12.5px;
  font-family: 'JetBrains Mono', Consolas, monospace;
  &.ok { background: #e7f6ec; color: #1a7f37; }
  &.fail { background: #fdeced; color: #b42318; }
  .td-err { color: #b42318; }
}
.ai-comment {
  margin-top: 10px;
  padding: 12px 14px;
  background: var(--el-color-primary-light-9);
  border-left: 3px solid var(--primary);
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.7;
}
@media (max-width: 860px) {
  .split {
    flex-direction: column;
  }
  .divider {
    display: none;
  }
  .pane.left {
    width: 100% !important;
    max-height: 40%;
  }
}
</style>
