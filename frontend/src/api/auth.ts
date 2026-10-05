import http from './http'

export interface TokenData {
  access_token: string
  token_type: string
  user_id: number
  username: string
  roles: string
}

export interface UserOut {
  id: number
  username: string
  email: string | null
  roles: string
  created_at: any
  last_login: any
}

export function login(payload: { username: string; password: string }): Promise<TokenData> {
  return http.post('/auth/login', payload)
}

export function register(payload: {
  username: string
  password: string
  email?: string
  roles: string
}): Promise<TokenData> {
  return http.post('/auth/register', payload)
}

export function me(): Promise<UserOut> {
  return http.get('/auth/me')
}

export function changePassword(payload: { old_password: string; new_password: string }) {
  return http.put('/auth/password', payload)
}
