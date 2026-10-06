import {
  useEffect,
  useState,
} from 'react'

import {
  useSearchParams,
} from 'react-router-dom'

import Header from '../components/Header'

import {
  getIncidents,
} from '../services/incidentService'

import {
  getIncidentTelemetry,
} from '../services/telemetryService'

import type {
  Incident,
} from '../types/incident'

import type {
  IncidentTelemetryResponse,
} from '../types/telemetry'


type TelemetryTab =
  | 'logs'
  | 'metrics'
  | 'deployments'


function formatTimestamp(
  timestamp: string,
) {
  const date = new Date(timestamp)

  if (Number.isNaN(date.getTime())) {
    return timestamp
  }

  return date.toLocaleString()
}


function TelemetryPage() {
  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams()

  const requestedIncidentId =
    searchParams.get('incident')

  const [
    incidents,
    setIncidents,
  ] = useState<Incident[]>([])

  const [
    incidentsLoading,
    setIncidentsLoading,
  ] = useState(true)

  const [
    incidentsError,
    setIncidentsError,
  ] = useState<string | null>(null)

  const [
    telemetry,
    setTelemetry,
  ] = useState<IncidentTelemetryResponse | null>(
    null,
  )

  const [
    loading,
    setLoading,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState<string | null>(null)

  const [
    activeTab,
    setActiveTab,
  ] = useState<TelemetryTab>('logs')


  // =========================
  // Incident Discovery
  // =========================

  useEffect(() => {
    let cancelled = false

    async function loadIncidents() {
      setIncidentsLoading(true)
      setIncidentsError(null)

      try {
        const result = await getIncidents()

        if (!cancelled) {
          setIncidents(result)
        }
      } catch (loadError) {
        if (!cancelled) {
          setIncidents([])

          setIncidentsError(
            loadError instanceof Error
              ? loadError.message
              : 'Unable to load incidents.',
          )
        }
      } finally {
        if (!cancelled) {
          setIncidentsLoading(false)
        }
      }
    }

    void loadIncidents()

    return () => {
      cancelled = true
    }
  }, [])


  // =========================
  // Telemetry Load
  // =========================

  useEffect(() => {
    if (!requestedIncidentId) {
      return
    }

    let cancelled = false

    async function loadTelemetry() {
      setLoading(true)
      setError(null)
      setTelemetry(null)

      try {
        const result =
          await getIncidentTelemetry(
            requestedIncidentId!,
          )

        if (!cancelled) {
          setTelemetry(result)
        }
      } catch (loadError) {
        if (!cancelled) {
          setTelemetry(null)

          setError(
            loadError instanceof Error
              ? loadError.message
              : 'Unable to load telemetry.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadTelemetry()

    return () => {
      cancelled = true
    }
  }, [requestedIncidentId])


  function handleIncidentChange(
    incidentId: string,
  ) {
    setActiveTab('logs')
    setTelemetry(null)
    setError(null)

    if (!incidentId) {
      setSearchParams({})
      return
    }

    setSearchParams({
      incident: incidentId,
    })
  }


  return (
    <div className="dashboard-page">
      <Header
        title="Telemetry"
        description="Inspect the production telemetry used by TraceRoot during incident investigations."
      />

      <div className="dashboard-content">
        <section className="incidents-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                Observability
              </p>

              <h2>
                {requestedIncidentId ??
                  'Telemetry Explorer'}
              </h2>

              <p>
                Raw telemetry available to the
                TraceRoot investigation engine.
              </p>
            </div>

            {telemetry && (
              <span className="section-meta">
                {telemetry.catalog.services.length}{' '}
                {telemetry.catalog.services.length === 1
                  ? 'service'
                  : 'services'}
              </span>
            )}
          </div>

          {/* =========================
              Incident Selector
          ========================== */}

          <div className="telemetry-catalog">
            <div>
              <span>Incident</span>

              {incidentsLoading ? (
                <strong>
                  Loading incidents...
                </strong>
              ) : incidentsError ? (
                <strong>
                  Unable to load incidents
                </strong>
              ) : (
                <select
                  value={requestedIncidentId ?? ''}
                  onChange={(event) =>
                    handleIncidentChange(
                      event.target.value,
                    )
                  }
                >
                  <option value="">
                    Select an incident
                  </option>

                  {incidents.map((incident) => (
                    <option
                      key={incident.id}
                      value={incident.id}
                    >
                      {incident.id} — {incident.title}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {!requestedIncidentId &&
            !incidentsLoading &&
            !incidentsError && (
              <div className="telemetry-state">
                Select an incident to inspect its
                telemetry.
              </div>
            )}

          {loading && (
            <div className="telemetry-state">
              Loading telemetry...
            </div>
          )}

          {!loading && error && (
            <div className="telemetry-state telemetry-state-error">
              <strong>
                Unable to load telemetry
              </strong>

              <p>{error}</p>
            </div>
          )}

          {requestedIncidentId &&
            !loading &&
            !error &&
            telemetry && (
              <>
                {/* =========================
                    Summary
                ========================== */}

                <div className="telemetry-summary-grid">
                  <article className="telemetry-summary-card">
                    <span>Logs</span>

                    <strong>
                      {telemetry.counts.logs}
                    </strong>
                  </article>

                  <article className="telemetry-summary-card">
                    <span>Metrics</span>

                    <strong>
                      {telemetry.counts.metrics}
                    </strong>
                  </article>

                  <article className="telemetry-summary-card">
                    <span>Deployments</span>

                    <strong>
                      {telemetry.counts.deployments}
                    </strong>
                  </article>

                  <article className="telemetry-summary-card">
                    <span>Services</span>

                    <strong>
                      {
                        telemetry.catalog.services
                          .length
                      }
                    </strong>
                  </article>
                </div>

                {/* =========================
                    Catalog
                ========================== */}

                <div className="telemetry-catalog">
                  <div>
                    <span>Services</span>

                    <strong>
                      {telemetry.catalog.services.length >
                      0
                        ? telemetry.catalog.services.join(
                            ', ',
                          )
                        : 'None'}
                    </strong>
                  </div>

                  <div>
                    <span>Log Levels</span>

                    <strong>
                      {telemetry.catalog.log_levels
                        .length > 0
                        ? telemetry.catalog.log_levels.join(
                            ', ',
                          )
                        : 'None'}
                    </strong>
                  </div>

                  <div>
                    <span>Metrics</span>

                    <strong>
                      {telemetry.catalog.metrics.length >
                      0
                        ? telemetry.catalog.metrics.join(
                            ', ',
                          )
                        : 'None'}
                    </strong>
                  </div>

                  <div>
                    <span>
                      Deployment Statuses
                    </span>

                    <strong>
                      {telemetry.catalog
                        .deployment_statuses.length >
                      0
                        ? telemetry.catalog.deployment_statuses.join(
                            ', ',
                          )
                        : 'None'}
                    </strong>
                  </div>
                </div>

                {/* =========================
                    Tabs
                ========================== */}

                <div
                  className="telemetry-tabs"
                  role="tablist"
                  aria-label="Telemetry sources"
                >
                  <button
                    type="button"
                    className={
                      activeTab === 'logs'
                        ? 'telemetry-tab telemetry-tab-active'
                        : 'telemetry-tab'
                    }
                    onClick={() =>
                      setActiveTab('logs')
                    }
                  >
                    Logs ({telemetry.counts.logs})
                  </button>

                  <button
                    type="button"
                    className={
                      activeTab === 'metrics'
                        ? 'telemetry-tab telemetry-tab-active'
                        : 'telemetry-tab'
                    }
                    onClick={() =>
                      setActiveTab('metrics')
                    }
                  >
                    Metrics (
                    {telemetry.counts.metrics})
                  </button>

                  <button
                    type="button"
                    className={
                      activeTab === 'deployments'
                        ? 'telemetry-tab telemetry-tab-active'
                        : 'telemetry-tab'
                    }
                    onClick={() =>
                      setActiveTab(
                        'deployments',
                      )
                    }
                  >
                    Deployments (
                    {telemetry.counts.deployments})
                  </button>
                </div>

                {/* =========================
                    Logs
                ========================== */}

                {activeTab === 'logs' && (
                  <div className="telemetry-record-list">
                    {telemetry.logs.length ===
                    0 ? (
                      <div className="telemetry-state">
                        No log telemetry available.
                      </div>
                    ) : (
                      telemetry.logs.map(
                        (log, index) => (
                          <article
                            key={`${log.timestamp}-${index}`}
                            className="telemetry-record"
                          >
                            <div className="telemetry-record-header">
                              <strong>
                                {log.service}
                              </strong>

                              <span className="telemetry-record-badge">
                                {log.level}
                              </span>

                              <time>
                                {formatTimestamp(
                                  log.timestamp,
                                )}
                              </time>
                            </div>

                            <p>
                              {log.message}
                            </p>
                          </article>
                        ),
                      )
                    )}
                  </div>
                )}

                {/* =========================
                    Metrics
                ========================== */}

                {activeTab === 'metrics' && (
                  <div className="telemetry-record-list">
                    {telemetry.metrics.length ===
                    0 ? (
                      <div className="telemetry-state">
                        No metric telemetry available.
                      </div>
                    ) : (
                      telemetry.metrics.map(
                        (metric, index) => (
                          <article
                            key={`${metric.timestamp}-${metric.metric}-${index}`}
                            className="telemetry-record"
                          >
                            <div className="telemetry-record-header">
                              <strong>
                                {metric.service}
                              </strong>

                              <span className="telemetry-record-badge">
                                {metric.metric}
                              </span>

                              <time>
                                {formatTimestamp(
                                  metric.timestamp,
                                )}
                              </time>
                            </div>

                            <div className="telemetry-metric-value">
                              {metric.value}
                            </div>
                          </article>
                        ),
                      )
                    )}
                  </div>
                )}

                {/* =========================
                    Deployments
                ========================== */}

                {activeTab ===
                  'deployments' && (
                  <div className="telemetry-record-list">
                    {telemetry.deployments.length ===
                    0 ? (
                      <div className="telemetry-state">
                        No deployment telemetry
                        available.
                      </div>
                    ) : (
                      telemetry.deployments.map(
                        (deployment) => (
                          <article
                            key={
                              deployment.deployment_id
                            }
                            className="telemetry-record telemetry-deployment-record"
                          >
                            <div className="telemetry-record-header">
                              <strong>
                                {
                                  deployment.service
                                }
                              </strong>

                              <span
                                className={`telemetry-deployment-status telemetry-deployment-status-${deployment.status.toLowerCase()}`}
                              >
                                {
                                  deployment.status
                                }
                              </span>

                              <time>
                                {formatTimestamp(
                                  deployment.timestamp,
                                )}
                              </time>
                            </div>

                            <div className="telemetry-deployment-details">
                              <div>
                                <span>
                                  Deployment ID
                                </span>

                                <strong>
                                  {
                                    deployment.deployment_id
                                  }
                                </strong>
                              </div>

                              <div>
                                <span>
                                  Version
                                </span>

                                <strong>
                                  {
                                    deployment.version
                                  }
                                </strong>
                              </div>

                              <div>
                                <span>
                                  Service
                                </span>

                                <strong>
                                  {
                                    deployment.service
                                  }
                                </strong>
                              </div>

                              <div>
                                <span>
                                  Status
                                </span>

                                <strong>
                                  {
                                    deployment.status
                                  }
                                </strong>
                              </div>
                            </div>
                          </article>
                        ),
                      )
                    )}
                  </div>
                )}
              </>
            )}
        </section>
      </div>
    </div>
  )
}

export default TelemetryPage