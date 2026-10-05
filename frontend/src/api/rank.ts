import http from './http'

export interface RankEntry {
  user_id: number
  username: string
  total_score: number
  passed_count: number
  submission_count: number
  avg_score: number
}

export function getRank(scope: 'class' | 'school' = 'class', classId?: number): Promise<{
  scope: string
  class_id: number | null
  entries: RankEntry[]
}> {
  return http.get('/rank', { params: { scope, class_id: classId } })
}
