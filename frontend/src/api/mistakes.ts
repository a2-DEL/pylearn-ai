import http from './http'

export interface MistakeOut {
  submission_id: number
  problem_id: number | null
  task_id: number | null
  knowledge_point: string
  code: string
  error_msg: string
  ai_comment: string
  score: number
  mode: string
  submitted_at: any
}

export interface LearningPathOut {
  user_id: number
  recommended: { slug: string; title: string; layer: string; difficulty: string; status: string; accuracy: number }[]
  weak_points: string[]
}

export function listMistakes(): Promise<MistakeOut[]> {
  return http.get('/mistakes')
}

export function learningPath(): Promise<LearningPathOut> {
  return http.get('/learning-path')
}
