export type InvestigationRequest = {
  incident_id: string
}

export type EvidenceResponse = {
  id: string
  source_type: string
  service: string
  content: string
  relevance_score: number
}

export type HypothesisResponse = {
  id: string
  description: string
  supporting_evidence: string[]
  contradicting_evidence: string[]
  confidence: number
  status: string
}

export type RootCauseResponse = {
  description: string
  supporting_evidence: string[]
  contradicting_evidence: string[]
  source_types: string[]
  confidence: number
  status: string
}

export type InvestigationResponse = {
  incident_id: string
  status: string
  iteration: number
  current_step: string
  executed_actions: string[]
  evidence: EvidenceResponse[]
  hypotheses: HypothesisResponse[]
  root_cause: RootCauseResponse | null
  final_report: string | null
  error: string | null
}

export type InvestigationHistoryItem = {
  investigation_id: string
  incident_id: string
  status: string
  iteration: number
  current_step: string
  created_at: string
  root_cause_confidence: number | null
}

export type InvestigationStreamEventType =
  | 'started'
  | 'progress'
  | 'completed'
  | 'investigation_error'

export type InvestigationStreamEvent = {
  event: InvestigationStreamEventType
  incident_id: string
  node?: string | null
  step?: string | null
  iteration?: number | null
  message: string
  data?: InvestigationResponse | null
}