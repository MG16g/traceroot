export type IncidentSeverity =
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'

export type IncidentStatus =
  | 'open'
  | 'investigating'
  | 'resolved'

export type IncidentCreateRequest = {
  id: string
  title: string
  description: string
  service: string
  severity: IncidentSeverity
  status: IncidentStatus
}

export type Incident = {
  id: string
  title: string
  description: string
  service: string
  severity: IncidentSeverity
  status: IncidentStatus
  created_at: string
}