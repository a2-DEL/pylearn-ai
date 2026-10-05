import http from './http'

export interface WorkOut {
  id: number
  user_id: number
  username: string
  problem_id: number | null
  problem_title: string
  task_id: number | null
  code: string
  score: number
  run_time: number
  submitted_at: any
  likes: number
}

export function listWorks(classId?: number): Promise<WorkOut[]> {
  return http.get('/works', { params: { class_id: classId } })
}

export function likeWork(id: number): Promise<{ likes: number }> {
  return http.post(`/works/${id}/like`)
}
