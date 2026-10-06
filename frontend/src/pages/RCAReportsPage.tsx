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
  getInvestigationHistory,
  getRCAReport,
} from '../services/investigationService'

import type {
  InvestigationHistoryItem,
  RCAReportSummary,
} from '../types/investigation'

const DEFAULT_INCIDENT_ID = 'INC-001'

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

  const [searchParams] =
    useSearchParams()

  const investigationId =
    searchParams.get('investigation')

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
  // Load Report Library
  // =========================

  useEffect(() => {
    let cancelled = false

    async function loadReports() {
      setReportsLoading(true)
      setReportsError(null)

      try {
        const history =
          await getInvestigationHistory(
            DEFAULT_INCIDENT_ID,
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
  }, [])

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

  function handleViewReport(
    selectedInvestigationId: string,
  ) {
    setReport(null)
    setReportError(null)

    navigate(
      `/rca-reports?investigation=${encodeURIComponent(
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

            {!reportsLoading &&
              !reportsError && (
                <span className="section-meta">
                  {reports.length}{' '}
                  {reports.length === 1
                    ? 'report'
                    : 'reports'}
                </span>
              )}
          </div>

          {/* =========================
              Library Loading
          ========================== */}

          {reportsLoading && (
            <div className="rca-page-state">
              Loading RCA reports...
            </div>
          )}

          {/* =========================
              Library Error
          ========================== */}

          {!reportsLoading &&
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

          {!reportsLoading &&
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
                  to={`/investigations?incident=${DEFAULT_INCIDENT_ID}`}
                  className="investigate-button"
                >
                  Start Investigation
                </Link>
              </div>
            )}

          {/* =========================
              Report Rows
          ========================== */}

          {!reportsLoading &&
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
                to={`/investigations?incident=${DEFAULT_INCIDENT_ID}`}
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