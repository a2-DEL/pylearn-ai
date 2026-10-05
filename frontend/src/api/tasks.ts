import http from './http'

export interface TaskOut {
  id: number
  class_id: number | null
  creator_id: number
  title: string
  description: string
  knowledge_point: string
  difficulty: string
  test_cases: { input: string; expected: string }[]
  hints: string[]
  deadline: any
  max_submissions: number
  allow_ai: boolean
  source: string
  created_at: any
}

export interface GradingResult {
  status: string
  passed: boolean
  score: number
  run_time: number
  error_msg: string
  ai_comment: string
  test_detail: any[]
  similar_flag: boolean
  submission_id?: number
}

export function createTask(payload: {
  class_id?: number | null
  title: string
  description: string
  knowledge_point: string
  difficulty: string
  test_cases: any[]
  hints: string[]
  deadline?: any
  max_submissions: number
  allow_ai: boolean
  source: string
}): Promise<TaskOut> {
  return http.post('/tasks', payload)
}

export function listTasks(params: { class_id?: number | null; bank?: boolean } = {}): Promise<TaskOut[]> {
  return http.get('/tasks', { params })
}

export function getTask(id: number): Promise<TaskOut> {
  return http.get(`/tasks/${id}`)
}

export function updateTask(id: number, payload: any): Promise<TaskOut> {
  return http.put(`/tasks/${id}`, payload)
}

export function deleteTask(id: number) {
  return http.delete(`/tasks/${id}`)
}

export function generateTasks(params: {
  major?: string
  knowledge?: string
  difficulty?: string
  count?: number
  class_id?: number | null
}): Promise<TaskOut[]> {
  return http.post('/tasks/generate', null, { params })
}

export function submitTask(id: number, payload: { code: string; mode: string; prompt?: string }): Promise<GradingResult> {
  return http.post(`/tasks/${id}/submit`, payload)
}

export function taskSubmissions(id: number) {
  return http.get(`/tasks/${id}/submissions`)
}
