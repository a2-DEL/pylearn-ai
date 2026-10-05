import http from './http'

export interface ClassOut {
  id: number
  teacher_id: number
  class_name: string
  major: string
  invite_code: string
  description: string
  status: string
  created_at: any
  student_count: number
}

export interface MemberOut {
  user_id: number
  username: string
  role: string
  group_name: string
  joined_at: any
}

export function createClass(payload: { class_name: string; major: string; description: string }): Promise<ClassOut> {
  return http.post('/classes', payload)
}

export function myClasses(): Promise<ClassOut[]> {
  return http.get('/classes/mine')
}

export function getClass(id: number): Promise<ClassOut> {
  return http.get(`/classes/${id}`)
}

export function updateClass(id: number, payload: Partial<{ class_name: string; major: string; description: string; status: string }>) {
  return http.put(`/classes/${id}`, payload)
}

export function archiveClass(id: number) {
  return http.post(`/classes/${id}/archive`)
}

export function resetInviteCode(id: number): Promise<{ invite_code: string }> {
  return http.post(`/classes/${id}/reset-code`)
}

export function joinClass(invite_code: string) {
  return http.post('/classes/join', { invite_code })
}

export function listMembers(id: number): Promise<MemberOut[]> {
  return http.get(`/classes/${id}/members`)
}

export function removeMember(classId: number, userId: number) {
  return http.delete(`/classes/${classId}/members/${userId}`)
}

export function setGroup(classId: number, userId: number, group: string) {
  return http.put(`/classes/${classId}/members/${userId}/group`, null, { params: { group } })
}

export function batchImport(classId: number, usernames: string[]) {
  return http.post(`/classes/${classId}/members/batch`, usernames, {
    headers: { 'Content-Type': 'application/json' },
  })
}
