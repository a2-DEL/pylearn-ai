import http from './http'

export function doCheckin(): Promise<{ date: string; streak: number; total: number }> {
  return http.post('/checkin')
}

export function listCheckins(userId?: number): Promise<string[]> {
  return http.get('/checkins', { params: { user_id: userId } })
}

export function listBadges(userId?: number): Promise<{
  id: number
  user_id: number
  badge_type: string
  badge_name: string
  reason: string
  created_at: any
}[]> {
  return http.get('/badges', { params: { user_id: userId } })
}
