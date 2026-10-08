import {
  useEffect,
  useState,
} from 'react'

import {
  Link,
  useNavigate,
  useSearchParams,
} from 'react-router-dom'

import Header from '../components/Header'
import RCAReportView from '../components/RCAReportView'

import {
  getIncidents,
} from '../services/incidentService'

import type {
  Incident,
} from '../types/incident'

import {
  getInvestigationHistory,
  getRCAReport,
} from '../services/investigationService'

import type {
  InvestigationHistoryItem,
  RCAReportSummary,
} from '../types/investigation'


function formatDate(timestamp: string) {
  const date = new Date(timestamp)

  if (Number.isNaN(date.getTime())) {
    return timestamp
  }

  return date.toLocaleString()
}

function formatConfidence(
  confidence: number | null,
) {
  if (confidence === null) {
    return 'No RCA'
  }

  return `${Math.round(
    confidence * 100,
  )}%`
}

function RCAReportsPage() {
  const navigate = useNavigate()

  const [
    searchParams,
    setSearchParams,
  ] = useSearchParams()

  const incidentId =
    searchParams.get('incident')

  const investigationId =
    searchParams.get('investigation')


  // =========================
  // Incident Discovery
  // =========================

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

  // =========================
  // Report Library
  // =========================

  const [
    reports,
    setReports,
  ] = useState<InvestigationHistoryItem[]>([])

  const [
    reportsLoading,
    setReportsLoading,
  ] = useState(false)

  const [
    reportsError,
    setReportsError,
  ] = useState<string | null>(null)

  // =========================
  // Selected RCA Report
  // =========================

  const [
    report,
    setReport,
  ] = useState<RCAReportSummary | null>(
    null,
  )

  const [
    reportLoading,
    setReportLoading,
  ] = useState(false)

  const [
    reportError,
    setReportError,
  ] = useState<string | null>(null)


  // =========================
  // Load Incidents
  // =========================

  useEffect(() => {
    let cancelled = false

    async function loadIncidents() {
      try {
        const result = await getIncidents()

        if (!cancelled) {
          setIncidents(result)
        }
      } catch (error) {
        if (!cancelled) {
          setIncidents([])

          setIncidentsError(
            error instanceof Error
              ? error.message
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
  // Load Report Library
  // =========================

  useEffect(() => {
    if (!incidentId) {
      return
    }

    const selectedIncidentId = incidentId

    let cancelled = false

    async function loadReports() {
      setReportsLoading(true)
      setReportsError(null)

      try {
        const history =
          await getInvestigationHistory(
            selectedIncidentId,
          )

        if (!cancelled) {
          setReports(history)
        }
      } catch (error) {
        if (!cancelled) {
          setReportsError(
            error instanceof Error
              ? error.message
              : 'Unable to load RCA reports.',
          )
        }
      } finally {
        if (!cancelled) {
          setReportsLoading(false)
        }
      }
    }

    void loadReports()

    return () => {
      cancelled = true
    }
  }, [incidentId])

  // =========================
  // Load Selected RCA Report
  // =========================

  useEffect(() => {
    if (!investigationId) {
      return
    }

    let cancelled = false

    async function loadReport() {
      setReportLoading(true)
      setReportError(null)

      try {
        const result =
          await getRCAReport(
            investigationId!,
          )

        if (!cancelled) {
          setReport(result)
        }
      } catch (error) {
        if (!cancelled) {
          setReport(null)

          setReportError(
            error instanceof Error
              ? error.message
              : 'Unable to load RCA report.',
          )
        }
      } finally {
        if (!cancelled) {
          setReportLoading(false)
        }
      }
    }

    void loadReport()

    return () => {
      cancelled = true
    }
  }, [investigationId])

  // =========================
  // Select Report
  // =========================

  function handleIncidentChange(
    selectedIncidentId: string,
  ) {
    setReports([])
    setReportsError(null)

    setReport(null)
    setReportError(null)

    if (!selectedIncidentId) {
      setSearchParams({})
      return
    }

    setSearchParams({
      incident: selectedIncidentId,
    })
  }

  function handleViewReport(
    selectedInvestigationId: string,
  ) {
    setReport(null)
    setReportError(null)

    if (!incidentId) {
  return
}

  navigate(
      `/rca-reports?incident=${encodeURIComponent(
        incidentId,
      )}&investigation=${encodeURIComponent(
        selectedInvestigationId,
      )}`,
    )
  }

  return (
    <div className="dashboard-page">
      <Header
        title="RCA Reports"
        description="Review persisted root-cause analysis reports from completed TraceRoot investigations."
      />

      <div className="dashboard-content">
        {/* =========================
            Report Library
        ========================== */}

        <section className="incidents-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                Report Library
              </p>

              <h2>
                Available RCA Reports
              </h2>

              <p>
                Root-cause reports generated
                from completed investigations.
              </p>
            </div>

            { incidentId &&
              !reportsLoading &&
              !reportsError && (
                <span className="section-meta">
                  {reports.length}{' '}
                  {reports.length === 1
                    ? 'report'
                    : 'reports'}
                </span>
              )}
          </div>

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
                  value={incidentId ?? ''}
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
                      {incident.id} {'—'} {incident.title}
                    </option>
                  ))}
                </select>
              )}
            </div>
          </div>

          {!incidentId &&
            !incidentsLoading &&
            !incidentsError && (
              <div className="rca-page-state rca-library-empty-state">
                <div className="rca-library-empty-icon" aria-hidden="true">
                  <svg
                    width="30"
                    height="30"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M8 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V8l-5-5h-4" />
                    <path d="M16 3v5h5" />
                    <path d="M8 13h8M8 17h6" />
                  </svg>
                </div>

                <h3>Explore Root Cause Reports</h3>

                <p>
                  Select an incident above to review investigation
                  findings, supporting evidence, and root-cause
                  analysis reports.
                </p>
              </div>
            )}

          {/* =========================
              Library Loading
          ========================== */}

          {incidentId &&
           reportsLoading && (
            <div className="rca-page-state">
              Loading RCA reports...
            </div>
          )}

          {/* =========================
              Library Error
          ========================== */}

          {incidentId &&
           !reportsLoading &&
            reportsError && (
              <div className="rca-page-state rca-page-state-error">
                <strong>
                  Unable to load reports
                </strong>

                <p>
                  {reportsError}
                </p>
              </div>
            )}

          {/* =========================
              Empty Library
          ========================== */}

          {incidentId &&
           !reportsLoading &&
            !reportsError &&
            reports.length === 0 && (
              <div className="rca-page-empty">
                <div>
                  <strong>
                    No RCA reports yet
                  </strong>

                  <p>
                    Run an investigation to
                    generate the first RCA
                    report.
                  </p>
                </div>

                <Link
                  to={
                    incidentId
                      ? `/investigations?incident=${encodeURIComponent(
                          incidentId,
                        )}`
                      : '/incidents'
                  }
                  className="investigate-button"
                >
                  Start Investigation
                </Link>
              </div>
            )}

          {/* =========================
              Report Rows
          ========================== */}

          { incidentId &&
            !reportsLoading &&
            !reportsError &&
            reports.length > 0 && (
              <div className="rca-library">
                {reports.map(
                  (historyItem) => {
                    const selected =
                      investigationId ===
                      historyItem.investigation_id

                    return (
                      <article
                        key={
                          historyItem.investigation_id
                        }
                        className={`rca-library-row${
                          selected
                            ? ' rca-library-row-selected'
                            : ''
                        }`}
                      >
                        <div className="rca-library-main">
                          <strong>
                            {
                              historyItem.investigation_id
                            }
                          </strong>

                          <span>
                            {
                              historyItem.incident_id
                            }
                          </span>
                        </div>

                        <div className="rca-library-meta">
                          <span>
                            {
                              historyItem.status
                            }
                          </span>

                          <span>
                            {
                              historyItem.iteration
                            }{' '}
                            {historyItem.iteration ===
                            1
                              ? 'iteration'
                              : 'iterations'}
                          </span>

                          <span>
                            {formatDate(
                              historyItem.created_at,
                            )}
                          </span>
                        </div>

                        <div className="rca-library-confidence">
                          <span>
                            RCA Confidence
                          </span>

                          <strong>
                            {formatConfidence(
                              historyItem.root_cause_confidence,
                            )}
                          </strong>
                        </div>

                        <button
                          type="button"
                          className="history-report-button"
                          disabled={selected}
                          onClick={() =>
                            handleViewReport(
                              historyItem.investigation_id,
                            )
                          }
                        >
                          {selected
                            ? 'Selected'
                            : 'View Report'}
                        </button>
                      </article>
                    )
                  },
                )}
              </div>
            )}
        </section>

        {/* =========================
            Selected Report
        ========================== */}

        {investigationId && (
          <section className="incidents-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">
                  Selected Report
                </p>

                <h2>
                  {investigationId}
                </h2>
              </div>

              <Link
                to={
                  incidentId
                    ? `/investigations?incident=${encodeURIComponent(
                        incidentId,
                      )}`
                    : '/investigations'
                }
                className="rca-back-link"
              >
                ← Back to Investigations
              </Link>
            </div>
          </section>
        )}

        {/* =========================
            Report Loading
        ========================== */}

        {investigationId &&
          reportLoading && (
            <div className="rca-page-state">
              <strong>
                Loading RCA report...
              </strong>

              <p>
                Retrieving the persisted
                investigation analysis.
              </p>
            </div>
          )}

        {/* =========================
            Report Error
        ========================== */}

        {investigationId &&
          !reportLoading &&
          reportError && (
            <div className="rca-page-state rca-page-state-error">
              <strong>
                Unable to load RCA report
              </strong>

              <p>
                {reportError}
              </p>
            </div>
          )}

        {/* =========================
            RCA Report
        ========================== */}

        {investigationId &&
          !reportLoading &&
          !reportError &&
          report && (
            <RCAReportView
              report={report}
            />
          )}

        {/* =========================
            Nothing Selected
        ========================== */}

        {!investigationId &&
          !reportsLoading &&
          !reportsError &&
          reports.length > 0 && (
            <div className="rca-page-state">
              <strong>
                Select an RCA report
              </strong>

              <p>
                Choose a report above to
                inspect its root cause,
                evidence, investigation
                actions, and generated
                analysis.
              </p>
            </div>
          )}
      </div>
    </div>
  )
}

export default RCAReportsPage