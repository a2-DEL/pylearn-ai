import http from './http'

export interface ProgressOut {
  id: number
  user_id: number
  knowledge_point: string
  status: string
  accuracy: number
  updated_at: any
}

export function upsertProgress(payload: { knowledge_point: string; status: string; accuracy: number }) {
  return http.put('/learning-progress', payload)
}

export function myProgress(): Promise<ProgressOut[]> {
  return http.get('/learning-progress')
}
