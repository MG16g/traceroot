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

export type InvestigationComparisonSide = {
  investigation_id: string
  incident_id: string
  created_at: string
  status: string
  iteration: number
  current_step: string
  action_count: number
  evidence_count: number
  hypothesis_count: number
  root_cause_confidence: number | null
  root_cause_status: string | null
}

export type InvestigationComparisonChanges = {
  confidence_delta: number | null
  iteration_delta: number
  action_count_delta: number
  evidence_count_delta: number
  hypothesis_count_delta: number
  status_changed: boolean
  root_cause_status_changed: boolean
  new_evidence_count: number
  removed_evidence_count: number
  new_hypothesis_count: number
  removed_hypothesis_count: number
}

export type InvestigationComparisonResponse = {
  baseline: InvestigationComparisonSide
  comparison: InvestigationComparisonSide
  changes: InvestigationComparisonChanges
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