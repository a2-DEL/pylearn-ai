import http from './http'

export interface MyStats {
  total_submissions: number
  passed: number
  pass_rate: number
  avg_score: number
  track_a: number
  track_b: number
  ai_dependency: number
  history: {
    id: number
    title: string
    status: string
    score: number
    mode: string
    submitted_at: string
  }[]
}

export function getMyStats(): Promise<MyStats> {
  return http.get('/me/stats')
}
