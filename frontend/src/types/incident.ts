export type IncidentSeverity = 'critical' | 'high' | 'medium' | 'low'
export type IncidentStatus = 'open' | 'investigating' | 'resolved'

export type Incident = {
  id: string
  title: string
  service: string
  severity: IncidentSeverity
  status: IncidentStatus
}