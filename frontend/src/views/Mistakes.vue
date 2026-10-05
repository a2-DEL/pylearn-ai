<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { LearningPathOut, MistakeOut, listMistakes, learningPath } from '@/api/mistakes'

const mistakes = ref<MistakeOut[]>([])
const path = ref<LearningPathOut | null>(null)
const loading = ref(false)

onMounted(load)

async function load() {
  loading.value = true
  try {
    const [m, p] = await Promise.all([listMistakes(), learningPath()])
    mistakes.value = m
    path.value = p
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

function statusText(s: string) {
  return { 未学: '未学习', 学习中: '学习中', 已掌握: '已掌握' }[s] || s
}
function statusType(s: string) {
  return { 未学: 'info', 学习中: 'warning', 已掌握: 'success' }[s] || 'info'
}
</script>

<template>
  <div class="py-container mistakes">
    <h2 class="py-section-title">错题本与个性化学习路径</h2>
    <p class="py-section-sub">自动聚合未通过或低分的提交，并基于你的学习进度推荐下一步该攻克的薄弱知识点。</p>

    <div class="grid">
      <div class="py-card list">
        <h4>我的错题（{{ mistakes.length }}）</h4>
        <el-skeleton v-if="loading" :rows="4" />
        <div v-else-if="!mistakes.length" class="empty">暂无错题，继续保持！</div>
        <div v-else class="mistake" v-for="m in mistakes" :key="m.submission_id">
          <div class="m-head">
            <el-tag size="small" type="danger">得分 {{ m.score }}</el-tag>
            <span class="kp" v-if="m.knowledge_point">{{ m.knowledge_point }}</span>
          </div>
          <pre class="code">{{ m.code.slice(0, 400) }}</pre>
          <p v-if="m.error_msg" class="err">{{ m.error_msg.slice(0, 200) }}</p>
          <p v-if="m.ai_comment" class="ai">{{ m.ai_comment.slice(0, 200) }}</p>
        </div>
      </div>

      <div class="py-card path">
        <h4>推荐学习路径</h4>
        <div v-if="path" class="weak">
          <span>薄弱点：</span>
          <el-tag v-for="w in path.weak_points" :key="w" size="small" type="warning" class="w">{{ w }}</el-tag>
        </div>
        <div v-if="path" class="rec">
          <div v-for="r in path.recommended" :key="r.slug" class="rec-item">
            <div class="rec-top">
              <b>{{ r.title }}</b>
              <el-tag size="small" :type="statusType(r.status)">{{ statusText(r.status) }}</el-tag>
            </div>
            <div class="rec-meta">
              <span>{{ r.layer }}</span><span>难度 {{ r.difficulty }}</span>
              <span>正确率 {{ Math.round(r.accuracy * 100) }}%</span>
            </div>
            <el-progress :percentage="Math.round(r.accuracy * 100)" :stroke-width="8" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.grid { display: grid; grid-template-columns: 1fr 0.8fr; gap: 22px; margin-top: 16px; }
.list, .path { padding: 18px 22px; }
.mistake { border: 1px solid rgba(31,42,61,0.08); border-radius: 12px; padding: 12px; margin-bottom: 12px; }
.m-head { display: flex; gap: 8px; align-items: center; margin-bottom: 8px; }
.kp { font-size: 12px; color: var(--text-sub); }
.code { background: #0f1b33; color: #e6edf7; padding: 10px; border-radius: 8px; font-size: 12px; max-height: 160px; overflow: auto; white-space: pre-wrap; }
.err { color: #ef4444; font-size: 12.5px; margin: 8px 0 0; }
.ai { color: var(--text-main); font-size: 12.5px; margin: 6px 0 0; line-height: 1.6; }
.empty { color: var(--text-sub); text-align: center; padding: 30px 0; }
.weak { margin-bottom: 14px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.w { margin-right: 4px; }
.rec-item { padding: 10px 0; border-bottom: 1px dashed rgba(31,42,61,0.08); }
.rec-top { display: flex; justify-content: space-between; align-items: center; }
.rec-meta { display: flex; gap: 14px; font-size: 12px; color: var(--text-sub); margin: 6px 0; }
@media (max-width: 980px) { .grid { grid-template-columns: 1fr; } }
</style>
