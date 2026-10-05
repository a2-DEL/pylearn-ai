import http from './http'

export interface ChatMsg {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export function chat(payload: {
  messages: ChatMsg[]
  provider?: string
  api_key?: string
  base_url?: string
  model?: string
  temperature?: number
  max_tokens?: number
}): Promise<{ content: string }> {
  return http.post('/ai/chat', { stream: false, ...payload })
}

export function explain(payload: {
  code: string
  error_msg?: string
  question?: string
  provider?: string
  api_key?: string
  base_url?: string
  model?: string
}): Promise<{ content: string }> {
  return http.post('/ai/explain', payload)
}

export function detectConfig(payload: {
  base_url: string
  api_key: string
}): Promise<{ provider: string; base_url: string; models: string[]; default_model: string }> {
  return http.post('/ai/detect', payload)
}

/**
 * SSE 流式对话：使用 fetch 消费 text/event-stream。
 * onToken 每收到一段文本触发；onDone 流结束触发；onError 出错触发。
 */
export async function streamChat(
  payload: {
    messages: ChatMsg[]
    provider?: string
    api_key?: string
    base_url?: string
    model?: string
    temperature?: number
    max_tokens?: number
  },
  handlers: { onToken: (t: string) => void; onDone?: () => void; onError?: (e: string) => void },
): Promise<void> {
  try {
    const resp = await fetch('/api/ai/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ stream: true, ...payload }),
    })
    if (!resp.body) throw new Error('无响应流')
    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      for (const block of lines) {
        const line = block.trim()
        if (!line.startsWith('data:')) continue
        const data = line.slice(5).trim()
        if (data === '[DONE]') {
          handlers.onDone?.()
          return
        }
        try {
          const obj = JSON.parse(data)
          if (obj.error) handlers.onError?.(obj.error)
          else if (obj.content) handlers.onToken(obj.content)
        } catch {
          /* ignore malformed */
        }
      }
    }
    handlers.onDone?.()
  } catch (e) {
    handlers.onError?.(String(e))
    handlers.onDone?.()
  }
}
