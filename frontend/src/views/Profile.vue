<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { RadarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useUserStore } from '@/stores/user'
import { myProgress, type ProgressOut } from '@/api/learningProgress'
import { getMyStats, type MyStats } from '@/api/me'

use([CanvasRenderer, RadarChart, TitleComponent, TooltipComponent, LegendComponent])

const router = useRouter()
const userStore = useUserStore()

const progress = ref<ProgressOut[]>([])
const stats = ref<MyStats | null>(null)

const radarOption = ref({
  tooltip: {},
  radar: {
    indicator: [
      { name: '基础语法', max: 100 },
      { name: '函数', max: 100 },
      { name: '面向对象', max: 100 },
      { name: '文件操作', max: 100 },
      { name: '数据分析', max: 100 },
      { name: '可视化', max: 100 },
    ],
    radius: '66%',
  },
  series: [
    {
      type: 'radar',
      data: [
        {
          value: [70, 60, 45, 50, 30, 25],
          name: '当前能力',
          areaStyle: { color: 'rgba(47,107,255,0.25)' },
          lineStyle: { color: '#2F6BFF' },
          itemStyle: { color: '#2F6BFF' },
        },
      ],
    },
  ],
})

onMounted(async () => {
  if (userStore.isLogin) {
    try {
      const [p, s] = await Promise.all([myProgress(), getMyStats()])
      progress.value = p
      stats.value = s
    } catch {
      /* ignore */
    }
  }
})

</script>

<template>
  <div class="py-container profile">
    <div class="profile-head py-card">
      <el-avatar :size="64" style="background: linear-gradient(120deg, #2f6bff, #00c2d1); font-size: 26px">
        {{ userStore.displayName.slice(0, 1) }}
      </el-avatar>
      <div class="head-info">
        <h2>{{ userStore.displayName }}</h2>
        <span class="role" v-if="userStore.isLogin">
          已登录 · 角色：{{ userStore.profile?.roles }}
          <el-button text type="primary" size="small" @click="router.push('/class-center')">我的班级</el-button>
        </span>
        <span class="role" v-else>
          游客模式
          <el-button text type="primary" size="small" @click="router.push('/login')">去登录 / 注册</el-button>
        </span>
      </div>
    </div>

    <div class="stat-grid">
      <div class="py-card stat">
        <div class="stat-val">{{ stats?.total_submissions ?? 0 }}<small>次</small></div>
        <div class="stat-label">总提交</div>
      </div>
      <div class="py-card stat">
        <div class="stat-val">{{ stats?.passed ?? 0 }}<small>次</small></div>
        <div class="stat-label">通过次数</div>
      </div>
      <div class="py-card stat">
        <div class="stat-val">{{ stats?.pass_rate ?? 0 }}<small>%</small></div>
        <div class="stat-label">通过率</div>
      </div>
      <div class="py-card stat">
        <div class="stat-val">{{ stats?.avg_score ?? 0 }}<small>分</small></div>
        <div class="stat-label">平均得分</div>
      </div>
    </div>

    <div class="py-card ai-dep" v-if="userStore.isLogin">
      <div class="dep-ring">
        <el-progress type="dashboard" :percentage="stats?.ai_dependency ?? 0" :width="110" :stroke-width="10" />
      </div>
      <div class="dep-info">
        <h3>AI 协作依赖度</h3>
        <p class="dep-desc">
          你 <b>{{ stats?.track_b ?? 0 }}</b> 次提交是借助 AI 完成的，占总提交的
          <b>{{ stats?.ai_dependency ?? 0 }}%</b>。
        </p>
        <p class="dep-tip" v-if="(stats?.ai_dependency ?? 0) > 60">
          ⚠️ 依赖度偏高。试试先自己写一版，再让 AI Review——这才是企业看重的 AI 协作方式。
        </p>
        <p class="dep-tip good" v-else-if="(stats?.ai_dependency ?? 0) > 0">
          👍 平衡得不错。独立写是基本功，AI 协作是放大器，两者都要练。
        </p>
        <p class="dep-tip good" v-else>
          🌱 你目前全部是独立写代码。可以试试「面试真题库」练 Prompt 指挥 AI 的能力。
        </p>
      </div>
    </div>

    <div class="py-card progress-card" v-if="userStore.isLogin">
      <h3>学习进度</h3>
      <div v-if="progress.length" class="prog-list">
        <div v-for="p in progress" :key="p.knowledge_point" class="prog-item">
          <span class="prog-name">{{ p.knowledge_point }}</span>
          <el-tag size="small" :type="p.status === '已掌握' ? 'success' : p.status === '学习中' ? 'warning' : 'info'">{{ p.status }}</el-tag>
          <span class="prog-acc">正确率 {{ p.accuracy }}%</span>
        </div>
      </div>
      <el-empty v-else description="暂无学习进度，去训练场练习吧" :image-size="60" />
    </div>

    <div class="mid">
      <div class="py-card chart-card">
        <h3>技能雷达图</h3>
        <v-chart :option="radarOption" class="chart" autoresize />
      </div>

      <div class="py-card hist-card">
        <h3>最近提交</h3>
        <div v-if="stats?.history?.length">
          <div v-for="h in stats.history" :key="h.id" class="hist-item">
            <span class="h-title">{{ h.title }}</span>
            <el-tag :type="h.status === 'success' ? 'success' : 'danger'" size="small">
              {{ h.status === 'success' ? '通过' : '未过' }}
            </el-tag>
            <el-tag v-if="h.mode === 'track_b'" type="warning" size="small">AI 协作</el-tag>
            <span class="h-score" v-if="h.status === 'success'">{{ h.score }} 分</span>
            <span class="h-time">{{ h.submitted_at?.slice(0, 16).replace('T', ' ') }}</span>
          </div>
        </div>
        <el-empty v-else description="暂无提交记录，去训练场写第一行代码吧" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.profile-head {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 22px 26px;
  margin-bottom: 18px;
}
.head-info h2 {
  margin: 0 0 4px;
  font-size: 22px;
}
.role {
  font-size: 12px;
  color: var(--text-sub);
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 18px;
}
.stat {
  padding: 20px;
  text-align: center;
}
.stat-val {
  font-size: 28px;
  font-weight: 700;
  color: var(--primary);
  small {
    font-size: 13px;
    color: var(--text-sub);
    margin-left: 4px;
    font-weight: 400;
  }
}
.stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-sub);
}
.ai-dep { display: flex; align-items: center; gap: 26px; padding: 22px 26px; margin-bottom: 18px; }
.dep-info h3 { margin: 0 0 8px; font-size: 16px; }
.dep-desc { color: var(--text-main); line-height: 1.7; margin: 0 0 8px; b { color: var(--primary); } }
.dep-tip { margin: 0; font-size: 13px; color: var(--warning); line-height: 1.6; }
.dep-tip.good { color: var(--success); }
.progress-card {
  padding: 22px 24px;
  margin-bottom: 18px;
  h3 {
    margin: 0 0 14px;
    font-size: 16px;
  }
}
.prog-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.prog-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid rgba(31, 42, 61, 0.06);
}
.prog-name {
  width: 160px;
  font-size: 13px;
  font-weight: 500;
}
.prog-acc {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-sub);
}
.mid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.chart-card,
.hist-card {
  padding: 22px 24px;
  h3 {
    margin: 0 0 14px;
    font-size: 16px;
  }
}
.chart {
  height: 320px;
}
.hist-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(31, 42, 61, 0.06);
  .h-title {
    font-weight: 500;
  }
  .h-score {
    font-size: 12px;
    color: var(--success);
  }
  .h-time {
    margin-left: auto;
    font-size: 12px;
    color: var(--text-sub);
  }
}
@media (max-width: 860px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .mid {
    grid-template-columns: 1fr;
  }
}
</style>
