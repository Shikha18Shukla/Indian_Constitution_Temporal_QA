import { API_BASE_URL, type CompareRequest, type ComparisonRun, type HealthResponse } from '../types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new Error('Cannot reach the API. Confirm the FastAPI server is running and the API base URL is correct.')
  }

  const payload = await response.json().catch(() => null)
  if (!response.ok) {
    const detail = payload?.detail
    const message = Array.isArray(detail)
      ? detail.map((item: { loc?: unknown[]; msg?: string }) => `${item.loc?.slice(-1)[0] ?? 'request'}: ${item.msg ?? 'invalid value'}`).join(' · ')
      : typeof detail === 'string'
        ? detail
        : `Request failed (${response.status} ${response.statusText})`
    throw new Error(message)
  }
  return payload as T
}

export const api = {
  health: () => request<HealthResponse>('/health'),
  compare: (body: CompareRequest) => request<ComparisonRun>('/compare', {
    method: 'POST',
    body: JSON.stringify(body),
  }),
  history: (limit = 20) => request<{ count: number; runs: ComparisonRun[] }>(`/history?limit=${limit}`),
}
