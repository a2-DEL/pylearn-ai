<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  getClass,
  listMembers,
  removeMember,
  setGroup,
  batchImport,
  resetInviteCode,
  archiveClass,
  type ClassOut,
  type MemberOut,
} from '@/api/classes'
import {
  listTasks,
  createTask,
  generateTasks,
  submitTask,
  type TaskOut,
} from '@/api/tasks'
import { classStats, exportClassCsv } from '@/api/stats'
import { teachingPlan } from '@/api/plans'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const classId = Number(route.params.id)

const cls = ref<ClassOut | null>(null)
const members = ref<MemberOut[]>([])
const tasks = ref<TaskOut[]>([])
const activeTab = ref('overview')
const isTeacher = computed(() => cls.value?.teacher_id === userStore.profile?.id)

const modeAPercent = computed(() => {
  if (!stats.value) return 0
  const { track_a = 0, track_b = 0 } = stats.value.overview || {}
  const total = track_a + track_b
  return total ? Math.round((track_a / total) * 100) : 50
})
const modeBPercent = computed(() => 100 - modeAPercent.value)

const loading = ref(false)

// 任务创建
const taskVisible = ref(false)
const genVisible = ref(false)
const newTask = ref({
  title: '',
  description: '',
  knowledge_point: '',
  difficulty: 'easy',
  allow_ai: true,
  max_submissions: 5,
  deadline: '',
  test_cases: [{ input: '', expected: '' }] as { input: string; expected: string }[],
  hints: '' as string,
})
const genForm = ref({ knowledge: '', difficulty: 'easy', count: 3 })
const submitting = ref(false)

// 统计
const stats = ref<any>(null)
// 教学方案
const planForm = ref({ major: '', goal: '', style: '' })
const planResult = ref<any>(null)
const planning = ref(false)

async function loadAll() {
  loading.value = true
  try {
    cls.value = await getClass(classId)
    members.value = await listMembers(classId)
    tasks.value = await listTasks({ class_id: classId })
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

async function onResetCode() {
  const r = await resetInviteCode(classId)
  cls.value!.invite_code = r.invite_code
  ElMessage.success('邀请码已重置')
}
async function onArchive() {
  await archiveClass(classId)
  ElMessage.success('班级已归档')
  await loadAll()
}

async function onRemove(m: MemberOut) {
  await removeMember(classId, m.user_id)
  ElMessage.success('已移除')
  await loadAll()
}
async function onSetGroup(m: MemberOut, group: string) {
  await setGroup(classId, m.user_id, group)
  ElMessage.success('已更新分组')
  await loadAll()
}
const batchText = ref('')
async function onBatch() {
  const names = batchText.value.split(/[\n,，]/).map((s) => s.trim()).filter(Boolean)
  if (!names.length) return
  await batchImport(classId, names)
  ElMessage.success('导入完成')
  batchText.value = ''
  await loadAll()
}

function addCase() {
  newTask.value.test_cases.push({ input: '', expected: '' })
}
function removeCase(i: number) {
  newTask.value.test_cases.splice(i, 1)
}

async function onCreateTask() {
  if (!newTask.value.title) {
    ElMessage.warning('请填写任务标题')
    return
  }
  submitting.value = true
  try {
    await createTask({
      class_id: classId,
      title: newTask.value.title,
      description: newTask.value.description,
      knowledge_point: newTask.value.knowledge_point,
      difficulty: newTask.value.difficulty,
      allow_ai: newTask.value.allow_ai,
      max_submissions: newTask.value.max_submissions,
      deadline: newTask.value.deadline || undefined,
      test_cases: newTask.value.test_cases.filter((c) => c.input && c.expected),
      hints: newTask.value.hints ? newTask.value.hints.split('\n').filter(Boolean) : [],
      source: 'custom',
    })
    ElMessage.success('任务已发布')
    taskVisible.value = false
    await loadAll()
  } catch {
    /* ignore */
  } finally {
    submitting.value = false
  }
}

async function onGenerate() {
  submitting.value = true
  try {
    await generateTasks({ ...genForm.value, class_id: classId })
    ElMessage.success('AI 已生成题目')
    genVisible.value = false
    await loadAll()
  } catch {
    /* ignore */
  } finally {
    submitting.value = false
  }
}

async function loadStats() {
  stats.value = await classStats(classId)
}
async function onExport() {
  const r = await exportClassCsv(classId)
  const blob = new Blob([r.csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = r.filename
  a.click()
  URL.revokeObjectURL(url)
}

async function onPlan() {
  planning.value = true
  try {
    const r = await teachingPlan(planForm.value)
    planResult.value = r
  } catch {
    /* ignore */
  } finally {
    planning.value = false
  }
}

function openTask(t: TaskOut) {
  router.push(`/practice?task=${t.id}`)
}

onMounted(loadAll)
</script>

<template>
  <div class="py-container class-detail" v-if="cls">
    <div class="cd-head">
      <div>
        <h2 class="py-section-title">{{ cls.class_name }}</h2>
        <p class="py-section-sub">{{ cls.major || '未设置专业' }} · 邀请码 <b class="code">{{ cls.invite_code }}</b> · {{ members.length }} 名学生</p>
      </div>
      <div class="cd-actions" v-if="isTeacher">
        <el-button @click="onResetCode">重置邀请码</el-button>
        <el-button type="primary" @click="taskVisible = true"><el-icon><Plus /></el-icon>&nbsp;发布任务</el-button>
        <el-button @click="onArchive">归档班级</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="cd-tabs">
      <!-- 概览 -->
      <el-tab-pane label="概览" name="overview">
        <div class="cd-cards">
          <div class="cd-stat py-card"><div class="num">{{ members.length }}</div><div class="lab">学生人数</div></div>
          <div class="cd-stat py-card"><div class="num">{{ tasks.length }}</div><div class="lab">任务数</div></div>
          <div class="cd-stat py-card" v-if="stats"><div class="num">{{ stats.overview.completion_rate }}%</div><div class="lab">完成率</div></div>
          <div class="cd-stat py-card" v-if="stats"><div class="num">{{ stats.overview.avg_score }}</div><div class="lab">平均分</div></div>
        </div>
        <div class="cd-tasks py-card">
          <h4>最近任务</h4>
          <div v-for="t in tasks.slice(0, 5)" :key="t.id" class="cd-task-row" @click="openTask(t)">
            <span>{{ t.title }}</span>
            <el-tag size="small" :type="t.difficulty === 'easy' ? 'success' : t.difficulty === 'medium' ? 'warning' : 'danger'">
              {{ t.difficulty }}
            </el-tag>
          </div>
          <el-empty v-if="!tasks.length" description="暂无任务" :image-size="60" />
        </div>
      </el-tab-pane>

      <!-- 学生管理 -->
      <el-tab-pane label="学生管理" name="students" v-if="isTeacher">
        <div class="cd-toolbar">
          <el-popover title="批量导入" trigger="click" width="320">
            <template #reference><el-button>批量导入</el-button></template>
            <el-input v-model="batchText" type="textarea" :rows="4" placeholder="用户名，逗号或换行分隔" />
            <el-button type="primary" size="small" style="margin-top: 8px" @click="onBatch">导入</el-button>
          </el-popover>
          <span class="hint">批量导入会按用户名自动建号，默认密码为邀请码。</span>
        </div>
        <el-table :data="members" class="py-card">
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="group_name" label="分组" width="160">
            <template #default="{ row }">
              <el-input v-model="row.group_name" size="small" @change="(v: string) => onSetGroup(row, v)" />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button text type="danger" size="small" @click="onRemove(row)">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 任务管理 -->
      <el-tab-pane label="任务管理" name="tasks">
        <div class="cd-toolbar" v-if="isTeacher">
          <el-button type="primary" @click="taskVisible = true">自定义题目</el-button>
          <el-button @click="genVisible = true"><el-icon><MagicStick /></el-icon>&nbsp;AI 生成题目</el-button>
        </div>
        <el-table :data="tasks" class="py-card">
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="knowledge_point" label="知识点" width="140" />
          <el-table-column prop="difficulty" label="难度" width="100" />
          <el-table-column prop="max_submissions" label="最大提交" width="100" />
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button text type="primary" size="small" @click="openTask(row)">去完成</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 数据统计 -->
      <el-tab-pane label="数据统计" name="stats" v-if="isTeacher">
        <div class="cd-toolbar">
          <el-button @click="loadStats">刷新数据</el-button>
          <el-button type="success" @click="onExport"><el-icon><Download /></el-icon>&nbsp;导出成绩 CSV</el-button>
        </div>
        <div v-if="stats" class="cd-stats">
          <div class="cd-cards">
            <div class="cd-stat py-card"><div class="num">{{ stats.overview.total_submissions }}</div><div class="lab">总提交</div></div>
            <div class="cd-stat py-card"><div class="num">{{ stats.overview.completion_rate }}%</div><div class="lab">完成率</div></div>
            <div class="cd-stat py-card"><div class="num">{{ stats.overview.avg_score }}</div><div class="lab">平均分</div></div>
          </div>
          <div class="py-card mode-split">
            <h4>独立编程 vs AI 协作（提交占比）</h4>
            <div class="mode-bar">
              <div class="mode-a" :style="{ width: modeAPercent + '%' }">独立编程 {{ stats.overview.track_a }}</div>
              <div class="mode-b" :style="{ width: modeBPercent + '%' }">AI 协作 {{ stats.overview.track_b }}</div>
            </div>
            <p class="mode-tip">AI 协作提交占比过高可能意味着学生在依赖 AI，建议结合课堂表现观察。</p>
          </div>
          <div class="py-card heat">
            <h4>知识点掌握热力（平均分）</h4>
            <div v-for="h in stats.heatmap" :key="h.knowledge_point" class="heat-row">
              <span class="heat-name">{{ h.knowledge_point }}</span>
              <div class="heat-bar"><div class="heat-fill" :style="{ width: h.avg_score + '%' }" :class="h.avg_score >= 80 ? 'good' : h.avg_score >= 60 ? 'mid' : 'low'"></div></div>
              <span class="heat-val">{{ h.avg_score }}</span>
            </div>
            <el-empty v-if="!stats.heatmap.length" description="暂无提交数据" :image-size="50" />
          </div>
          <div class="py-card warns">
            <h4>学困生预警</h4>
            <div v-for="w in stats.warnings" :key="w.user_id" class="warn-row">
              <el-tag type="danger" size="small">预警</el-tag>
              <span>用户 #{{ w.user_id }}：{{ w.reason }}</span>
            </div>
            <el-empty v-if="!stats.warnings.length" description="暂无预警" :image-size="50" />
          </div>
        </div>
        <el-empty v-else description="点击「刷新数据」加载看板" />
      </el-tab-pane>

      <!-- AI 教学方案 -->
      <el-tab-pane label="AI 教学方案" name="plan" v-if="isTeacher">
        <div class="py-card plan">
          <el-form label-width="90px" style="max-width: 560px">
            <el-form-item label="专业"><el-input v-model="planForm.major" placeholder="如：市场营销" /></el-form-item>
            <el-form-item label="培养目标"><el-input v-model="planForm.goal" type="textarea" :rows="2" placeholder="希望学生能用 Python 做用户画像分析和营销数据可视化" /></el-form-item>
            <el-form-item label="风格"><el-input v-model="planForm.style" placeholder="偏实战 / 重理论" /></el-form-item>
            <el-button type="primary" :loading="planning" @click="onPlan"><el-icon><MagicStick /></el-icon>&nbsp;生成方案</el-button>
          </el-form>
          <div v-if="planResult" class="plan-result">
            <h4>模块权重</h4>
            <el-table :data="Object.entries(planResult.weights || {}).map(([k, v]) => ({ k, v }))" size="small">
              <el-table-column prop="k" label="模块" />
              <el-table-column prop="v" label="权重" />
            </el-table>
            <h4>分阶段计划</h4>
            <ol><li v-for="(s, i) in planResult.stages || []" :key="i">{{ s.stage }} · {{ s.title }}（{{ s.weeks }}周）：{{ s.goals }}</li></ol>
            <h4>配套案例包</h4>
            <div v-for="(c, i) in planResult.cases || []" :key="i" class="case-item">
              <b>{{ c.title }}</b> — {{ c.scenario }}
            </div>
            <h4>考核建议</h4>
            <p>{{ planResult.assessment }}</p>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 自定义题目 -->
    <el-dialog v-model="taskVisible" title="发布任务（自定义）" width="640px">
      <el-form label-width="90px">
        <el-form-item label="标题"><el-input v-model="newTask.title" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="newTask.description" type="textarea" :rows="3" /></el-form-item>
        <el-form-item label="知识点"><el-input v-model="newTask.knowledge_point" placeholder="如 two_sum" /></el-form-item>
        <el-form-item label="难度">
          <el-select v-model="newTask.difficulty"><el-option label="简单" value="easy" /><el-option label="中等" value="medium" /><el-option label="较难" value="hard" /></el-select>
        </el-form-item>
        <el-form-item label="最大提交"><el-input-number v-model="newTask.max_submissions" :min="1" :max="20" /></el-form-item>
        <el-form-item label="允许 AI"><el-switch v-model="newTask.allow_ai" /></el-form-item>
        <el-form-item label="截止时间"><el-date-picker v-model="newTask.deadline" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" /></el-form-item>
        <el-form-item label="测试用例">
          <div class="cases-editor">
            <div v-for="(c, i) in newTask.test_cases" :key="i" class="case-line">
              <el-input v-model="c.input" placeholder="调用表达式，如 two_sum([2,7],9)" />
              <el-input v-model="c.expected" placeholder="期望结果，如 [0,1]" />
              <el-button text type="danger" @click="removeCase(i)">删</el-button>
            </div>
            <el-button @click="addCase">+ 添加用例</el-button>
          </div>
        </el-form-item>
        <el-form-item label="提示"><el-input v-model="newTask.hints" type="textarea" :rows="2" placeholder="每行一条提示" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onCreateTask">发布</el-button>
      </template>
    </el-dialog>

    <!-- AI 生成题目 -->
    <el-dialog v-model="genVisible" title="AI 生成题目" width="460px">
      <el-form label-width="80px">
        <el-form-item label="知识点"><el-input v-model="genForm.knowledge" placeholder="如 函数 / 数据分析" /></el-form-item>
        <el-form-item label="难度">
          <el-select v-model="genForm.difficulty"><el-option label="简单" value="easy" /><el-option label="中等" value="medium" /><el-option label="较难" value="hard" /></el-select>
        </el-form-item>
        <el-form-item label="数量"><el-input-number v-model="genForm.count" :min="1" :max="10" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="genVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="onGenerate">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.cd-head { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 16px; }
.cd-actions { display: flex; gap: 10px; }
.code { font-family: monospace; color: var(--primary); letter-spacing: 2px; }
.cd-cards { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
.cd-stat { padding: 18px 24px; min-width: 120px; text-align: center; }
.cd-stat .num { font-size: 26px; font-weight: 700; color: var(--primary); }
.cd-stat .lab { font-size: 12px; color: var(--text-sub); margin-top: 4px; }
.cd-tasks { padding: 18px 22px; }
.cd-tasks h4 { margin: 0 0 12px; }
.cd-task-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 0; border-bottom: 1px dashed rgba(31,42,61,0.08); cursor: pointer; }
.cd-task-row:hover { color: var(--primary); }
.cd-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.hint { font-size: 12px; color: var(--text-sub); }
.heat { padding: 18px 22px; margin-bottom: 16px; }
.heat h4, .warns h4, .plan h4 { margin: 0 0 12px; }
.heat-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.heat-name { width: 120px; font-size: 13px; }
.heat-bar { flex: 1; height: 12px; background: #eef1f6; border-radius: 6px; overflow: hidden; }
.heat-fill { height: 100%; border-radius: 6px; }
.heat-fill.good { background: #2bb673; }
.heat-fill.mid { background: #e0a93b; }
.heat-fill.low { background: #d9534f; }
.heat-val { width: 40px; text-align: right; font-size: 13px; color: var(--text-sub); }
.warns { padding: 18px 22px; }
.warn-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; font-size: 13px; }
.plan-result { margin-top: 18px; border-top: 1px dashed rgba(31,42,61,0.1); padding-top: 14px; }
.case-item { padding: 6px 0; font-size: 13px; }
.cases-editor .case-line { display: flex; gap: 8px; margin-bottom: 8px; align-items: center; }
.mode-split { padding: 18px 22px; margin-bottom: 16px; }
.mode-split h4 { margin: 0 0 12px; }
.mode-bar { display: flex; height: 36px; border-radius: 10px; overflow: hidden; font-size: 13px; font-weight: 600; color: #fff; }
.mode-a { background: linear-gradient(120deg, #2f6bff, #1e4fd6); display: flex; align-items: center; justify-content: center; min-width: 60px; }
.mode-b { background: linear-gradient(120deg, #f59e0b, #d97706); display: flex; align-items: center; justify-content: center; min-width: 60px; }
.mode-tip { margin: 10px 0 0; font-size: 12px; color: var(--text-sub); }
</style>
