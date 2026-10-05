import http from './http'

export function teachingPlan(payload: { major: string; goal: string; style: string }) {
  return http.post('/plans/teaching', payload)
}

export function promptTrain(payload: {
  requirement: string
  prompt: string
  provider?: string
  api_key?: string
  base_url?: string
  model?: string
}): Promise<any> {
  return http.post('/plans/prompt-train', payload)
}

// ---- 双轨 B 模式 3：代码审查找 bug 训练 ----
export interface DebugChallenge {
  id: number
  title: string
  difficulty: string
  description: string
  buggy_code: string
}

export function listDebugChallenges(): Promise<DebugChallenge[]> {
  return http.get('/plans/debug-train')
}

export function submitDebugFix(
  challengeId: number,
  code: string,
): Promise<{
  passed: boolean
  score: number
  bugs_found: number
  bugs_missed: string[]
  test_detail: any[]
  comment: string
  reference_revealed: boolean
  reference_code: string
}> {
  return http.post(`/plans/debug-train/${challengeId}/submit`, { code })
}

// ---- AI 学习规划师 ----
export function learningAdvisor(payload: {
  major: string
  level: string
  goal: string
}): Promise<{
  summary: string
  module_weights: Record<string, number>
  steps: { phase: string; focus: string; suggested_weeks: number }[]
  recommended_cases: string[]
  tips: string
}> {
  return http.post('/learning-advisor', payload)
}

// ---- 企业 AI Coding 面试真题库 ----
export interface InterviewQuestion {
  id: number
  title: string
  difficulty: string
  category: string
  requirement: string
}

export function listInterviewQuestions(): Promise<InterviewQuestion[]> {
  return http.get('/plans/interview/list')
}

export function submitInterview(qid: number, prompt: string): Promise<{
  generated_code: string
  case_results: { call: string; expected: string; passed: boolean }[]
  passed: number
  total: number
  hints_hit: string[]
  hints_total: string[]
  score: number
  comment: string
  sandbox_stdout: string
}> {
  return http.post(`/plans/interview/${qid}/submit`, { prompt })
}
