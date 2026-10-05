<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { learningAdvisor } from '@/api/plans'

const form = reactive({ major: '', level: '零基础', goal: '' })
const loading = ref(false)
const result = ref<Awaited<ReturnType<typeof learningAdvisor>> | null>(null)

const levels = ['零基础', '会一点基础语法', '能写简单脚本']

async function run() {
  loading.value = true
  result.value = null
  try {
    result.value = await learningAdvisor({
      major: form.major,
      level: form.level,
      goal: form.goal,
    })
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

const maxWeight = (w: Record<string, number>) => Math.max(1, ...Object.values(w))
</script>

<template>
  <div class="py-container advisor">
    <h2 class="py-section-title">AI 学习规划师</h2>
    <p class="py-section-sub">
      告诉它你的专业、当前水平和目标，AI 为你定制一条学习路线：哪些模块要重点学、分几个阶段、练什么案例。
    </p>

    <div class="ad-grid">
      <div class="py-card">
        <el-form label-position="top">
          <el-form-item label="你的专业 / 背景">
            <el-input v-model="form.major" placeholder="例如：金融学大二、市场营销、计算机大三、行政在职" />
          </el-form-item>
          <el-form-item label="当前水平">
            <el-radio-group v-model="form.level">
              <el-radio v-for="l in levels" :key="l" :value="l">{{ l }}</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="学习目标">
            <el-input
              v-model="form.goal"
              type="textarea"
              :rows="3"
              placeholder="例如：用 Python 做量化分析 / 写爬虫爬招聘信息 / 办公自动化处理 Excel"
            />
          </el-form-item>
          <el-button type="primary" :loading="loading" @click="run">
            <el-icon><MagicStick /></el-icon>&nbsp;生成我的学习地图
          </el-button>
        </el-form>
      </div>

      <div class="ad-right" v-if="result">
        <div class="py-card summary">
          <p>{{ result.summary }}</p>
        </div>

        <div class="py-card">
          <h4>模块权重</h4>
          <div v-for="(w, name) in result.module_weights" :key="name" class="weight-row">
            <span class="w-name">{{ name }}</span>
            <el-progress
              :percentage="(w / maxWeight(result.module_weights)) * 100"
              :stroke-width="10"
            />
            <span class="w-val">{{ w }}</span>
          </div>
        </div>

        <div class="py-card">
          <h4>分阶段计划</h4>
          <el-timeline>
            <el-timeline-item
              v-for="(s, i) in result.steps"
              :key="i"
              :timestamp="`约 ${s.suggested_weeks} 周`"
            >
              <b>{{ s.phase }}</b> — {{ s.focus }}
            </el-timeline-item>
          </el-timeline>
        </div>

        <div class="py-card">
          <h4>推荐案例</h4>
          <el-tag v-for="c in result.recommended_cases" :key="c" class="case-tag">{{ c }}</el-tag>
          <p class="tip">💡 {{ result.tips }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.ad-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 22px; margin-top: 16px; align-items: start; }
.ad-right > .py-card { margin-bottom: 16px; }
.summary p { line-height: 1.8; font-size: 14px; }
.weight-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.w-name { width: 110px; font-size: 13px; }
.w-val { width: 30px; text-align: right; font-size: 13px; color: var(--primary); }
.case-tag { margin: 0 8px 8px 0; }
.tip { margin-top: 12px; color: var(--text-sub); font-size: 13px; }
@media (max-width: 980px) { .ad-grid { grid-template-columns: 1fr; } }
</style>
