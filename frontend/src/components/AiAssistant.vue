<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { streamChat, explain, type ChatMsg } from '@/api/ai'
import { useAiConfigStore } from '@/stores/aiConfig'

const props = defineProps<{
  code: string
  errorMsg?: string
}>()

const aiStore = useAiConfigStore()
const messages = ref<ChatMsg[]>([])
const input = ref('')
const streaming = ref(false)

function pushAssistant(): ChatMsg {
  const m: ChatMsg = { role: 'assistant', content: '' }
  messages.value.push(m)
  return m
}

async function send() {
  const text = input.value.trim()
  if (!text || streaming.value) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''
  streaming.value = true
  const assistant = pushAssistant()
  const params = aiStore.buildChatParams()
  await streamChat(
    { messages: messages.value.slice(0, -1) as ChatMsg[], ...params },
    {
      onToken: (t) => {
        assistant.content += t
      },
      onError: (e) => {
        assistant.content += `\n\n（出错：${e}）`
      },
      onDone: () => {
        streaming.value = false
      },
    },
  )
}

async function askExplain() {
  if (streaming.value) return
  const params = aiStore.buildChatParams()
  const assistant = pushAssistant()
  streaming.value = true
  try {
    const res = await explain({
      code: props.code,
      error_msg: props.errorMsg || '',
      question: '请解释错误原因并给出修改思路（不要直接给完整代码）',
      ...params,
    })
    // 逐字显示，增强流式观感
    for (const ch of res.content) {
      assistant.content += ch
      await new Promise((r) => setTimeout(r, 8))
    }
  } catch (e) {
    assistant.content += `\n\n（出错：${String(e)}）`
  } finally {
    streaming.value = false
  }
}

function clearChat() {
  messages.value = []
}

defineExpose({ askExplain })
</script>

<template>
  <div class="ai-assistant">
    <div class="ai-head">
      <div class="ai-title">
        <el-icon><ChatDotRound /></el-icon>
        <span>AI 助手</span>
      </div>
      <el-button text size="small" @click="clearChat">清空</el-button>
    </div>

    <div class="ai-body">
      <div v-if="messages.length === 0" class="ai-empty">
        <el-icon :size="28"><MagicStick /></el-icon>
        <p>遇到报错或思路卡壳？向 AI 提问吧。</p>
        <el-button type="primary" plain size="small" :disabled="streaming" @click="askExplain">
          解释当前代码报错
        </el-button>
      </div>
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="bubble"
        :class="m.role"
      >
        <div class="bubble-role">{{ m.role === 'user' ? '我' : 'AI' }}</div>
        <pre class="bubble-text">{{ m.content || '思考中…' }}</pre>
      </div>
    </div>

    <div class="ai-input">
      <el-input
        v-model="input"
        type="textarea"
        :rows="2"
        resize="none"
        placeholder="输入你的问题，Enter 发送 / Shift+Enter 换行"
        @keydown.enter.exact.prevent="send"
      />
      <el-button type="primary" :loading="streaming" @click="send">发送</el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.ai-assistant {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.ai-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid rgba(31, 42, 61, 0.08);
}
.ai-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--primary);
}
.ai-body {
  flex: 1;
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ai-empty {
  margin: auto;
  text-align: center;
  color: var(--text-sub);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  p {
    margin: 4px 0;
    font-size: 13px;
  }
}
.bubble {
  max-width: 92%;
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.6;
  .bubble-role {
    font-size: 11px;
    opacity: 0.7;
    margin-bottom: 4px;
  }
  .bubble-text {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    font-family: inherit;
  }
}
.bubble.user {
  align-self: flex-end;
  background: linear-gradient(120deg, #2f6bff, #1e4fd6);
  color: #fff;
}
.bubble.assistant {
  align-self: flex-start;
  background: var(--el-color-primary-light-9);
  color: var(--text-main);
  border: 1px solid rgba(47, 107, 255, 0.12);
}
.ai-input {
  border-top: 1px solid rgba(31, 42, 61, 0.08);
  padding: 10px 12px;
  display: flex;
  gap: 8px;
  align-items: flex-end;
}
</style>
