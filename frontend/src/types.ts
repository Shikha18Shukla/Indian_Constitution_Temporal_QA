export type SystemId = 'A' | 'B' | 'C'
export type RunStatus = 'completed' | 'failed' | 'abstained' | string

export interface Citation {
  citation_id: string
  evidence: Evidence | null
  found_in_retrieved_evidence: boolean
}

export interface Evidence {
  chunk_id?: string
  chunk_text?: string
  text?: string
  source_document?: string
  source_locator?: string
  source_reference?: Record<string, unknown>
  source_section?: string
  page_number?: number | string
  article_number?: string
  version_id?: string
  effective_from?: string
  effective_to?: string | null
  evidence_coverage?: { verified_through?: string }
  evidence_verified_through?: string
  verification_status?: string
  retrieval_score?: number
  [key: string]: unknown
}

export interface EffectiveInterval {
  version_id: string
  effective_from: string
  effective_to: string | null
  evidence_verified_through?: string
}

export interface SystemResult {
  system: SystemId
  status: RunStatus
  answer: string | null
  citations: Citation[]
  retrieved_evidence: Evidence[]
  prompt_evidence: Evidence[]
  elapsed_seconds: number
  error: string | null
  abstention_reason: string | null
  model_name?: string | null
  generation_settings?: Record<string, unknown> | null
  retrieval_used?: boolean | null
  temporal_filtering_used?: boolean | null
  requested_article_identifier?: string | null
  selected_version_id?: string | null
  selected_version_ids: string[]
  effective_dates: EffectiveInterval[]
  verification_statuses: Array<{ version_id: string; status: string }>
  evidence_coverage: Array<{ version_id: string; verified_through?: string }>
  retrieval_elapsed_seconds?: number | null
  generation_elapsed_seconds?: number | null
}

export interface ComparisonRun {
  comparison_id: string
  created_at: string
  question: string
  reference_date: string
  systems: Partial<Record<SystemId, SystemResult>>
}

export interface HealthResponse {
  status: 'ok' | 'degraded' | string
  all_systems_available: boolean
  systems_available: Record<SystemId, boolean>
  gemini_api_key_configured: boolean
  availability_note?: string
}

export interface CompareRequest {
  question: string
  reference_date: string
  systems: SystemId[]
}

const envBase = import.meta.env.VITE_API_BASE_URL?.trim()
export const API_BASE_URL = (envBase || '/api').replace(/\/$/, '')
