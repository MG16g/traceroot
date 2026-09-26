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