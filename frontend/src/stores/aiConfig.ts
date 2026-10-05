import { defineStore } from 'pinia'
import { ref } from 'vue'
import { decryptConfig, encryptConfig } from '@/utils/crypto'

const STORAGE_KEY = 'pylearn_ai_config'

export interface AiConfig {
  provider: string
  api_key: string
  base_url: string
  default_model: string
  temperature: number
  max_tokens: number
  is_synced: boolean
  scene_models: Record<string, string>
  proxy: string
}

function defaultConfig(): AiConfig {
  return {
    provider: 'auto',
    api_key: '',
    base_url: '',
    default_model: '',
    temperature: 0.3,
    max_tokens: 1024,
    is_synced: false,
    scene_models: {},
    proxy: '',
  }
}

export const useAiConfigStore = defineStore('aiConfig', () => {
  const config = ref<AiConfig>(load())
  const hasKey = ref<boolean>(!!config.value.api_key)

  function load(): AiConfig {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return defaultConfig()
    try {
      return { ...defaultConfig(), ...(decryptConfig(raw) as AiConfig) }
    } catch {
      return defaultConfig()
    }
  }

  function save() {
    localStorage.setItem(STORAGE_KEY, encryptConfig(config.value))
    hasKey.value = !!config.value.api_key
  }

  function reset() {
    config.value = defaultConfig()
    localStorage.removeItem(STORAGE_KEY)
    hasKey.value = false
  }

  function buildChatParams() {
    const c = config.value
    return {
      provider: c.provider,
      api_key: c.api_key,
      base_url: c.base_url,
      model: c.default_model,
      temperature: c.temperature,
      max_tokens: c.max_tokens,
    }
  }

  return { config, hasKey, save, reset, load, buildChatParams }
})
