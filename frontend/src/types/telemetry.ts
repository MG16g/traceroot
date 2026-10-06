export type TelemetryCatalog = {
  services: string[]
  log_levels: string[]
  metrics: string[]
  deployment_statuses: string[]
}

export type TelemetryCounts = {
  logs: number
  metrics: number
  deployments: number
}

export type LogTelemetryRecord = {
  timestamp: string
  service: string
  level: string
  message: string
  [key: string]: unknown
}

export type MetricTelemetryRecord = {
  timestamp: string
  service: string
  metric: string
  value: number
  [key: string]: unknown
}

export type DeploymentTelemetryRecord = {
  deployment_id: string
  service: string
  version: string
  timestamp: string
  status: string
  [key: string]: unknown
}

export type IncidentTelemetryResponse = {
  incident_id: string
  catalog: TelemetryCatalog
  counts: TelemetryCounts
  logs: LogTelemetryRecord[]
  metrics: MetricTelemetryRecord[]
  deployments: DeploymentTelemetryRecord[]
}