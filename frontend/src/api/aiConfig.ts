import http from './http'

export interface AiConfigPayload {
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

export interface AiConfigOut {
  id: number
  user_id: number
  provider: string
  api_key_masked: string
  base_url: string
  default_model: string
  temperature: number
  max_tokens: number
  is_synced: boolean
  scene_models: Record<string, string>
  proxy: string
}

export function createAiConfig(payload: AiConfigPayload): Promise<AiConfigOut> {
  return http.post('/ai-config', payload)
}

export function listAiConfigs(userId = 0): Promise<AiConfigOut[]> {
  return http.get('/ai-config', { params: { user_id: userId } })
}

export function updateAiConfig(id: number, payload: Partial<AiConfigPayload>): Promise<AiConfigOut> {
  return http.put(`/ai-config/${id}`, payload)
}

export function deleteAiConfig(id: number): Promise<{ message: string }> {
  return http.delete(`/ai-config/${id}`)
}

export function testConnection(payload: {
  provider: string
  api_key: string
  base_url: string
  default_model: string
  proxy: string
}): Promise<{ success: boolean; message: string; models: string[] }> {
  return http.post('/ai-config/test', payload)
}
