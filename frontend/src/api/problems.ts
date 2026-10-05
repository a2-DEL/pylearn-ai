import http from './http'

export interface Problem {
  id: number
  title: string
  difficulty: string
  knowledge_point: string
  description: string
  example_input: string
  example_output: string
  test_cases: { input: string; expected: string }[]
  hints: string[]
}

export function listProblems(params?: {
  difficulty?: string
  knowledge_point?: string
}): Promise<Problem[]> {
  return http.get('/problems', { params: params || {} })
}

export function getProblem(id: number): Promise<Problem> {
  return http.get(`/problems/${id}`)
}
