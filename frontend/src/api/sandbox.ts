import http from './http'

export interface RunResult {
  stdout: string
  stderr: string
  run_time: number
  success: boolean
  error: string
}

export function runCode(payload: {
  code: string
  problem_id?: number | null
  enable_network?: boolean
  language?: string
}): Promise<RunResult> {
  return http.post('/sandbox/run', payload)
}
