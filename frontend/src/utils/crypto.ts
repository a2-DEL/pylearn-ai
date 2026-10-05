// 前端 AI 配置 AES 加密存储（localStorage 键 pylearn_ai_config）
// 盐需与后端 FRONTEND_AES_SALT 保持一致即可（仅前端本地存储用途）
import CryptoJS from 'crypto-js'

const SALT = 'pylearn-ai-salt'

export function encryptConfig(plain: unknown): string {
  return CryptoJS.AES.encrypt(JSON.stringify(plain), SALT).toString()
}

export function decryptConfig(cipher: string): unknown {
  const bytes = CryptoJS.AES.decrypt(cipher, SALT)
  return JSON.parse(bytes.toString(CryptoJS.enc.Utf8))
}

export function maskApiKey(key: string): string {
  if (!key) return ''
  if (key.length <= 4) return '****'
  return `****${key.slice(-4)}`
}
