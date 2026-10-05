import http from './http'

export interface ReviewResult {
  comments: string
  complexity: string
  risks: string[]
  score: number
}

export function reviewCode(payload: {
  code: string
  language?: string
  provider?: string
  api_key?: string
  base_url?: string
  model?: string
}): Promise<ReviewResult> {
  return http.post('/ai/review', payload)
}

export function tutorChat(payload: {
  message: string
  history?: { role: string; content: string }[]
  knowledge_point?: string
  provider?: string
  api_key?: string
  base_url?: string
  model?: string
}): Promise<{ content: string }> {
  return http.post('/ai/tutor', payload)
}
