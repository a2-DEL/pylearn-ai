<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import CodeEditor from '@/components/CodeEditor.vue'
import { reviewCode, tutorChat } from '@/api/review'
import { useUserStore } from '@/stores/user'
import { useAiConfigStore } from '@/stores/aiConfig'

const userStore = useUserStore()
const aiStore = useAiConfigStore()

const messages = ref<{ role: string; content: string }[]>([])
const input = ref('')
const sending = ref(false)
const knowledgePoint = ref('')

// 代码评审
const reviewDrawer = ref(false)
const reviewCodeText = ref('print("hello world")')
const reviewing = ref(false)
const reviewResult = ref<{ comments: string; complexity: string; risks: string[]; score: number } | null>(null)

function visitorParams() {
  return userStore.isLogin ? {} : aiStore.buildChatParams()
}

async function send() {
  const text = input.value.trim()
  if (!text || sending.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  sending.value = true
  const history = messages.value.slice(0, -1).map((m) => ({ role: m.role, content: m.content }))
  try {
    // 优先使用服务端 SSE 流式陪练
    const ok = await streamTutor(text, history)
    if (!ok) {
      const data = await tutorChat({ message: text, history, knowledge_point: knowledgePoint.value, ...visitorParams() })
      messages.value.push({ role: 'assistant', content: data.content })
    }
  } catch {
    /* ignore */
  } finally {
    sending.value = false
  }
}

async function streamTutor(text: string, history: any[]): Promise<boolean> {
  const params: any = { message: text, history, knowledge_point: knowledgePoint.value, stream: true, ...visitorParams() }
  let body = 'message=' + encodeURIComponent(params.message)
  body += '&history=' + encodeURIComponent(JSON.stringify(params.history))
  if (params.knowledge_point) body += '&knowledge_point=' + encodeURIComponent(params.knowledge_point)
  for (const k of ['provider', 'api_key', 'base_url', 'model']) {
    if (params[k]) body += `&${k}=` + encodeURIComponent(params[k])
  }
  try {
    const resp = await fetch('/api/ai/tutor/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', Authorization: `Bearer ${userStore.token}` },
      body,
    })
    if (!resp.body) return false
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buf = ''
    let acc = ''
    messages.value.push({ role: 'assistant', content: '' })
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buf += decoder.decode(value, { stream: true })
      const parts = buf.split('\n\n')
      buf = parts.pop() || ''
      for (const p of parts) {
        const line = p.trim()
        if (!line.startsWith('data:')) continue
        const json = line.slice(5).trim()
        if (json === '[DONE]') continue
        try {
          const obj = JSON.parse(json)
          if (obj.content) {
            acc += obj.content
            messages.value[messages.value.length - 1].content = acc
          }
        } catch {
          /* ignore */
        }
      }
    }
    return true
  } catch {
    messages.value.pop()
    return false
  }
}

async function runReview() {
  if (!reviewCodeText.value.trim()) return
  reviewing.value = true
  reviewResult.value = null
  try {
    reviewResult.value = await reviewCode({ code: reviewCodeText.value, language: 'python', ...visitorParams() })
  } catch {
    /* ignore */
  } finally {
    reviewing.value = false
  }
}

const canSend = computed(() => !!input.value.trim() && !sending.value)
</script>

<template>
  <div class="py-container tutor">
    <h2 class="py-section-title">AI 陪练 · 对话式答疑与代码评审</h2>
    <p class="py-section-sub">像有一位耐心的编程老师：用引导式对话帮你理清思路，也能对代码做专业评审与重构建议。</p>

    <div class="tutor-grid">
      <div class="py-card chat-card">
        <div class="chat-head">
          <el-input v-model="knowledgePoint" size="small" placeholder="当前知识点（可选，如：函数/列表推导）" class="kp" />
        </div>
        <div class="chat-body">
          <div v-if="!messages.length" class="empty">还没有对话，试着问：「Python 列表推导式怎么用？」</div>
          <div v-for="(m, i) in messages" :key="i" class="bubble" :class="m.role">
            <div class="who">{{ m.role === 'user' ? '我' : '陪练' }}</div>
            <div class="text">{{ m.content }}</div>
          </div>
          <div v-if="sending" class="bubble assistant"><div class="who">陪练</div><div class="text">思考中…</div></div>
        </div>
        <div class="chat-input">
          <el-input v-model="input" type="textarea" :rows="2" placeholder="输入你的问题…" @keyup.enter.ctrl="send" />
          <el-button type="primary" :disabled="!canSend" :loading="sending" @click="send">发送</el-button>
        </div>
      </div>

      <div class="py-card review-card">
        <div class="review-head">
          <h4>代码评审</h4>
          <el-button text type="primary" @click="reviewDrawer = true">放大编辑</el-button>
        </div>
        <div class="review-editor">
          <CodeEditor v-model="reviewCodeText" language="python" :read-only="false" />
        </div>
        <el-button type="primary" :loading="reviewing" @click="runReview">开始评审</el-button>
        <div v-if="reviewResult" class="review-out">
          <el-tag :type="reviewResult.score >= 80 ? 'success' : 'warning'">质量分 {{ reviewResult.score }}</el-tag>
          <p v-if="reviewResult.complexity"><b>复杂度：</b>{{ reviewResult.complexity }}</p>
          <div class="md" v-html="reviewResult.comments.replace(/\n/g, '<br/>')" />
          <div v-if="reviewResult.risks.length" class="risks">
            <el-tag v-for="r in reviewResult.risks" :key="r" type="danger" size="small" class="risk">{{ r }}</el-tag>
          </div>
        </div>
      </div>
    </div>

    <el-drawer v-model="reviewDrawer" title="代码评审（放大）" size="60%">
      <CodeEditor v-model="reviewCodeText" language="python" :read-only="false" style="height: 60vh" />
      <el-button type="primary" :loading="reviewing" @click="runReview">开始评审</el-button>
    </el-drawer>
  </div>
</template>

<style scoped lang="scss">
.tutor-grid { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 22px; margin-top: 16px; }
.chat-card { display: flex; flex-direction: column; height: 70vh; }
.chat-head { margin-bottom: 10px; }
.chat-body { flex: 1; overflow: auto; padding: 8px 4px; }
.empty { color: var(--text-sub); text-align: center; margin-top: 40px; }
.bubble { margin-bottom: 14px; max-width: 86%; }
.bubble.user { margin-left: auto; text-align: right; }
.bubble .who { font-size: 11px; color: var(--text-sub); margin-bottom: 4px; }
.bubble .text { display: inline-block; padding: 10px 14px; border-radius: 12px; line-height: 1.6; white-space: pre-wrap; text-align: left; }
.bubble.user .text { background: linear-gradient(120deg, #2f6bff, #1e4fd6); color: #fff; }
.bubble.assistant .text { background: #eef2ff; color: var(--text-main); }
.chat-input { display: flex; gap: 10px; align-items: flex-end; margin-top: 10px; }
.chat-input .el-button { flex-shrink: 0; }
.review-card { display: flex; flex-direction: column; }
.review-editor { height: 240px; margin: 10px 0; border: 1px solid rgba(31,42,61,0.1); border-radius: 12px; overflow: hidden; }
.review-head { display: flex; justify-content: space-between; align-items: center; }
.review-out { margin-top: 14px; }
.md { background: #f7f9fc; border-radius: 10px; padding: 12px; font-size: 13px; line-height: 1.7; }
.risks { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; }
@media (max-width: 980px) { .tutor-grid { grid-template-columns: 1fr; } }
</style>
