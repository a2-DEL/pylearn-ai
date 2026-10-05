import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as loginApi, register as registerApi, me as meApi, type TokenData, type UserOut } from '@/api/auth'

const TOKEN_KEY = 'pylearn_token'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const profile = ref<UserOut | null>(null)

  const isLogin = computed(() => !!token.value)
  const isTeacher = computed(() => !!profile.value?.roles.split(',').includes('teacher'))
  const displayName = computed(() => profile.value?.username || '游客')

  function setToken(t: string) {
    token.value = t
    if (t) localStorage.setItem(TOKEN_KEY, t)
    else localStorage.removeItem(TOKEN_KEY)
  }

  async function login(username: string, password: string) {
    const data = await loginApi({ username, password })
    setToken(data.access_token)
    profile.value = { id: data.user_id, username: data.username, email: null, roles: data.roles, created_at: null, last_login: null }
    return data
  }

  async function register(payload: { username: string; password: string; email?: string; roles: string }) {
    const data = await registerApi(payload)
    setToken(data.access_token)
    profile.value = { id: data.user_id, username: data.username, email: payload.email || null, roles: data.roles, created_at: null, last_login: null }
    return data
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      profile.value = await meApi()
    } catch {
      setToken('')
    }
  }

  function logout() {
    setToken('')
    profile.value = null
  }

  function hasRole(role: string) {
    return !!profile.value?.roles.split(',').includes(role)
  }

  return { token, profile, isLogin, isTeacher, displayName, login, register, fetchMe, logout, setToken, hasRole }
})

export type { TokenData, UserOut }
