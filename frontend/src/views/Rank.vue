<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RankEntry, getRank } from '@/api/rank'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const scope = ref<'class' | 'school'>('class')
const classId = ref<number | undefined>(undefined)
const entries = ref<RankEntry[]>([])
const loading = ref(false)

onMounted(load)

async function load() {
  loading.value = true
  try {
    const data = await getRank(scope.value, classId.value)
    entries.value = data.entries
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

function rankClass(i: number) {
  return i === 0 ? 'gold' : i === 1 ? 'silver' : i === 2 ? 'bronze' : ''
}
</script>

<template>
  <div class="py-container rank">
    <h2 class="py-section-title">学习排行榜</h2>
    <p class="py-section-sub">按提交成绩聚合排名，激励持续练习。可切换班级榜与全校榜。</p>

    <div class="toolbar">
      <el-radio-group v-model="scope" @change="load">
        <el-radio-button value="class">班级榜</el-radio-button>
        <el-radio-button value="school">全校榜</el-radio-button>
      </el-radio-group>
      <el-button :loading="loading" @click="load">刷新</el-button>
    </div>

    <div class="py-card board">
      <el-skeleton v-if="loading" :rows="6" />
      <div v-else-if="!entries.length" class="empty">暂无排名数据</div>
      <div v-else class="row" v-for="(e, i) in entries" :key="e.user_id" :class="rankClass(i)">
        <span class="no">{{ i + 1 }}</span>
        <span class="name">{{ e.username }}<i v-if="e.user_id === userStore.profile?.id">（我）</i></span>
        <span class="bar">
          <el-progress :percentage="Math.min(100, e.total_score)" :stroke-width="12" :show-text="false" />
        </span>
        <span class="score">{{ e.total_score }}</span>
        <span class="sub">提交 {{ e.submission_count }} · 通过 {{ e.passed_count }} · 均分 {{ e.avg_score }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.toolbar { display: flex; gap: 12px; align-items: center; margin: 16px 0; }
.board { padding: 18px 22px; }
.row { display: grid; grid-template-columns: 40px 140px 1fr 70px; gap: 14px; align-items: center; padding: 10px 0; border-bottom: 1px solid rgba(31,42,61,0.06); }
.row .no { font-weight: 700; color: var(--text-sub); text-align: center; }
.row.gold .no { color: #f59e0b; }
.row.silver .no { color: #94a3b8; }
.row.bronze .no { color: #b45309; }
.name { font-weight: 600; }
.name i { color: var(--primary); font-style: normal; font-size: 12px; }
.score { font-weight: 700; color: var(--primary); text-align: right; }
.sub { grid-column: 2 / 5; font-size: 12px; color: var(--text-sub); }
.empty { color: var(--text-sub); text-align: center; padding: 30px 0; }
</style>
