<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { doCheckin, listBadges, listCheckins } from '@/api/checkin'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const dates = ref<string[]>([])
const streak = ref(0)
const total = ref(0)
const badges = ref<{ id: number; badge_type: string; badge_name: string; reason: string; created_at: any }[]>([])
const checking = ref(false)

onMounted(load)

async function load() {
  const [d, b] = await Promise.all([listCheckins(), listBadges()])
  dates.value = d
  badges.value = b
  // 连续天数本地计算
  const set = new Set(d)
  let s = 0
  const cur = new Date()
  while (set.has(fmt(cur))) {
    s++
    cur.setDate(cur.getDate() - 1)
  }
  streak.value = s
  total.value = d.length
}

function fmt(dt: Date) {
  return dt.toISOString().slice(0, 10)
}

async function onCheckin() {
  checking.value = true
  try {
    const r = await doCheckin()
    streak.value = r.streak
    total.value = r.total
    if (!dates.value.includes(r.date)) dates.value.push(r.date)
    ElMessage.success(`打卡成功，连续 ${r.streak} 天`)
  } catch {
    /* ignore */
  } finally {
    checking.value = false
  }
}

// 最近 35 天日历格子
const calendar = computed(() => {
  const arr: { day: string; on: boolean }[] = []
  const today = new Date()
  for (let i = 34; i >= 0; i--) {
    const dt = new Date(today)
    dt.setDate(today.getDate() - i)
    const day = fmt(dt)
    arr.push({ day, on: dates.value.includes(day) })
  }
  return arr
})
</script>

<template>
  <div class="py-container checkin">
    <h2 class="py-section-title">学习打卡与徽章</h2>
    <p class="py-section-sub">坚持每日练习，连续打卡可获得徽章，记录你的成长轨迹。</p>

    <div class="grid">
      <div class="py-card cal">
        <div class="cal-head">
          <div>
            <div class="big">{{ total }}</div>
            <div class="sub">累计打卡（天）</div>
          </div>
          <div>
            <div class="big streak">{{ streak }}</div>
            <div class="sub">当前连续</div>
          </div>
          <el-button type="primary" :loading="checking" @click="onCheckin">今日打卡</el-button>
        </div>
        <div class="cells">
          <div v-for="c in calendar" :key="c.day" class="cell" :class="{ on: c.on }" :title="c.day" />
        </div>
      </div>

      <div class="py-card badge-wall">
        <h4>徽章墙</h4>
        <div v-if="!badges.length" class="empty">还没有徽章，去打卡或完成满分作业吧！</div>
        <div v-else class="badges">
          <div v-for="b in badges" :key="b.id" class="badge">
            <div class="ico">🏅</div>
            <div class="bn">{{ b.badge_name }}</div>
            <div class="br">{{ b.reason }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.grid { display: grid; grid-template-columns: 1.3fr 0.7fr; gap: 22px; margin-top: 16px; }
.cal, .badge-wall { padding: 18px 22px; }
.cal-head { display: flex; align-items: center; gap: 28px; margin-bottom: 16px; }
.big { font-size: 30px; font-weight: 700; color: var(--text-main); }
.big.streak { color: var(--primary); }
.sub { font-size: 12px; color: var(--text-sub); }
.cells { display: grid; grid-template-columns: repeat(7, 1fr); gap: 6px; }
.cell { aspect-ratio: 1; border-radius: 8px; background: #eef2ff; }
.cell.on { background: linear-gradient(120deg, #2f6bff, #1e4fd6); }
.badges { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; }
.badge { width: 120px; text-align: center; padding: 12px; border-radius: 12px; background: #f7f9fc; }
.ico { font-size: 26px; }
.bn { font-weight: 600; margin: 4px 0; }
.br { font-size: 11px; color: var(--text-sub); }
.empty { color: var(--text-sub); text-align: center; padding: 24px 0; }
@media (max-width: 980px) { .grid { grid-template-columns: 1fr; } }
</style>
