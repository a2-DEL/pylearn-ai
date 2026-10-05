import http from './http'

export interface KnowledgePoint {
  id: number
  layer: string
  category: string
  slug: string
  title: string
  content: string
  example_code: string
  difficulty: string
  order_index: number
}

export function listKnowledge(layer?: string): Promise<KnowledgePoint[]> {
  return http.get('/knowledge', { params: layer ? { layer } : {} })
}

export function getKnowledge(id: number): Promise<KnowledgePoint> {
  return http.get(`/knowledge/${id}`)
}
