import http from './http'

export interface PluginOut {
  name: string
  display_name: string
  version: string
  description: string
  category: string
  enabled: boolean
  config: Record<string, any>
}

export function listPlugins(): Promise<PluginOut[]> {
  return http.get('/plugins')
}

export function updatePlugin(
  name: string,
  payload: { enabled?: boolean; config?: Record<string, any> },
): Promise<PluginOut> {
  return http.put(`/plugins/${name}`, payload)
}
