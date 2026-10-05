<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { WorkOut, likeWork, listWorks } from '@/api/works'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const works = ref<WorkOut[]>([])
const loading = ref(false)
const reviewWork = ref<WorkOut | null>(null)
const reviewVisible = ref(false)
const reviewScore = ref(5)
const reviewComment = ref('')
const reviewList = ref<{ reviewer_name: string; score: number; comment: string }[]>([])

onMounted(load)

async function load() {
  loading.value = true
  try {
    works.value = await listWorks()
  } catch {
    /* ignore */
  } finally {
    loading.value = false
  }
}

async function like(w: WorkOut) {
  try {
    const r = await likeWork(w.id)
    w.likes = r.likes
  } catch {
    /* ignore */
  }
}

function openReview(w: WorkOut) {
  reviewWork.value = w
  reviewVisible.value = true
  reviewScore.value = 5
  reviewComment.value = ''
  reviewList.value = []
}

async function submitReview() {
  if (!reviewWork.value) return
  // 复用互评接口（后端），此处简化为本地展示 + 提示
  ElMessage.info('互评已记录（演示）')
  reviewList.value.push({ reviewer_name: userStore.displayName, score: reviewScore.value, comment: reviewComment.value })
  reviewWork.value = null
  reviewVisible.value = false
}
</script>

<template>
  <div class="py-container works">
    <h2 class="py-section-title">作品墙</h2>
    <p class="py-section-sub">展示通过评测的公开作品，为你欣赏的代码点赞，并在互评中交流思路。</p>

    <el-button :loading="loading" @click="load" class="refresh">刷新</el-button>

    <el-skeleton v-if="loading" :rows="6" />
    <div v-else-if="!works.length" class="empty">还没有公开作品，去训练场提交一个吧！</div>
    <div v-else class="masonry">
      <div class="py-card work" v-for="w in works" :key="w.id">
        <div class="w-head">
          <b>{{ w.problem_title || ('提交 #' + w.id) }}</b>
          <el-tag size="small" type="success">+{{ w.score }}</el-tag>
        </div>
        <div class="author">{{ w.username }} · {{ (w.run_time ?? 0).toFixed(2) }}s</div>
        <pre class="code">{{ w.code.slice(0, 300) }}</pre>
        <div class="w-foot">
          <el-button text @click="like(w)">👍 赞 {{ w.likes }}</el-button>
          <el-button text type="primary" @click="openReview(w)">互评</el-button>
        </div>
      </div>
    </div>

    <el-dialog v-model="reviewVisible" title="作品互评" width="460px">
      <template v-if="reviewWork">
        <pre class="code lg">{{ reviewWork.code.slice(0, 500) }}</pre>
        <el-rate v-model="reviewScore" :max="5" show-score />
        <el-input v-model="reviewComment" type="textarea" :rows="3" placeholder="写下你的评价…" class="mt" />
        <div v-if="reviewList.length" class="reviews">
          <div v-for="(r, i) in reviewList" :key="i" class="rv">
            <b>{{ r.reviewer_name }}</b> · {{ r.score }} 分：{{ r.comment }}
          </div>
        </div>
      </template>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview">提交互评</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.refresh { margin: 14px 0; }
.masonry { columns: 3; column-gap: 16px; margin-top: 8px; }
.work { break-inside: avoid; margin-bottom: 16px; padding: 14px 16px; }
.w-head { display: flex; justify-content: space-between; align-items: center; }
.author { font-size: 12px; color: var(--text-sub); margin: 6px 0; }
.code { background: #0f1b33; color: #e6edf7; padding: 10px; border-radius: 8px; font-size: 11.5px; white-space: pre-wrap; max-height: 180px; overflow: auto; }
.code.lg { max-height: 260px; margin-bottom: 12px; }
.w-foot { display: flex; justify-content: space-between; margin-top: 8px; }
.mt { margin-top: 12px; }
.reviews { margin-top: 12px; }
.rv { font-size: 12.5px; padding: 6px 0; border-top: 1px dashed rgba(31,42,61,0.08); }
.empty { color: var(--text-sub); text-align: center; padding: 30px 0; }
@media (max-width: 1100px) { .masonry { columns: 2; } }
@media (max-width: 720px) { .masonry { columns: 1; } }
</style>
