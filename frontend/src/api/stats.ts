import http from './http'

export function classStats(id: number) {
  return http.get(`/stats/class/${id}`)
}

export function exportClassCsv(id: number): Promise<{ filename: string; csv: string }> {
  return http.get(`/stats/class/${id}/export`)
}
