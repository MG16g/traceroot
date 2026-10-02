import { useEffect, useRef, useState } from 'react'

import Header from '../components/Header'
import StatCard from '../components/StatCard'
import IncidentTable from '../components/IncidentTable'
import InvestigationPanel from '../components/InvestigationPanel'
import InvestigationError from '../components/InvestigationError'
import InvestigationTimeline from '../components/InvestigationTimeline'
import InvestigationHistory from '../components/InvestigationHistory'
import InvestigationComparison from '../components/InvestigationComparison'
import RCAReportView from '../components/RCAReportView'

import {
  getInvestigationComparison,
  getInvestigationHistory,
  getInvestigationRun,
  streamInvestigation,
  getRCAReport,
} from '../services/investigationService'

import type { Incident } from '../types/incident'
import type {
  InvestigationComparisonResponse,
  InvestigationHistoryItem,
  InvestigationResponse,
  InvestigationStreamEvent,
  RCAReportSummary,
} from '../types/investigation'


const overviewStats = [
  {
    label: 'Active Incidents',
    value: 1,
    detail: 'Currently open',
    tone: 'warning' as const,
  },
  {
    label: 'Critical Incidents',
    value: 1,
    detail: 'Requires attention',
    tone: 'critical' as const,
  },
  {
    label: 'Investigations',
    value: 1,
    detail: 'Investigation records',
    tone: 'default' as const,
  },
  {
    label: 'Supported RCAs',
    value: 1,
    detail: 'Evidence supported',
    tone: 'success' as const,
  },
]


const incidents: Incident[] = [
  {
    id: 'INC-001',
    title: 'Checkout payment failures',
    service: 'payment-service',
    severity: 'critical',
    status: 'open',
  },
]


function DashboardPage() {
  const [
    investigatingIncidentId,
    setInvestigatingIncidentId,
  ] = useState<string | null>(null)

  const [
    investigationResult,
    setInvestigationResult,
  ] = useState<InvestigationResponse | null>(null)

  const [
    investigationError,
    setInvestigationError,
  ] = useState<string | null>(null)

  const [
    failedIncidentId,
    setFailedIncidentId,
  ] = useState<string | null>(null)

  const [
    streamEvents,
    setStreamEvents,
  ] = useState<InvestigationStreamEvent[]>([])

  const [
    investigationHistory,
    setInvestigationHistory,
  ] = useState<InvestigationHistoryItem[]>([])

  const [
    historyLoading,
    setHistoryLoading,
  ] = useState(true)

  const [
    historyError,
    setHistoryError,
  ] = useState<string | null>(null)

  const [
    historyDetailLoading,
    setHistoryDetailLoading,
  ] = useState(false)

  const [
    historyDetailError,
    setHistoryDetailError,
  ] = useState<string | null>(null)

  const [
    baselineInvestigationId,
    setBaselineInvestigationId,
  ] = useState<string>('')

  const [
    comparisonInvestigationId,
    setComparisonInvestigationId,
  ] = useState<string>('')

  const [
    investigationComparison,
    setInvestigationComparison,
  ] = useState<InvestigationComparisonResponse | null>(
    null,
  )

  const [
    comparisonLoading,
    setComparisonLoading,
  ] = useState(false)

  const [
    comparisonError,
    setComparisonError,
  ] = useState<string | null>(null)

  const [
    selectedRCAReport,
    setSelectedRCAReport,
  ] = useState<RCAReportSummary | null>(
    null,
  )

  const [
    rcaReportLoading,
    setRCAReportLoading,
  ] = useState(false)

  const [
    rcaReportError,
    setRCAReportError,
  ] = useState<string | null>(null)

  const eventSourceRef =
    useRef<EventSource | null>(null)


  // =========================
  // Refresh Investigation History
  // =========================

  async function refreshInvestigationHistory(
    showLoading = false,
  ) {
    if (showLoading) {
      setHistoryLoading(true)
    }

    setHistoryError(null)

    try {
      const history =
        await getInvestigationHistory(
          'INC-001',
        )

      setInvestigationHistory(
        history,
      )
    } catch (error) {
      setHistoryError(
        error instanceof Error
          ? error.message
          : 'Unable to load investigation history.',
      )
    } finally {
      if (showLoading) {
        setHistoryLoading(false)
      }
    }
  }


  // =========================
  // Initial History Load
  // =========================

  useEffect(() => {
    let cancelled = false

    async function loadInitialHistory() {
      setHistoryLoading(true)
      setHistoryError(null)

      try {
        const history =
          await getInvestigationHistory(
            'INC-001',
          )

        if (!cancelled) {
          setInvestigationHistory(
            history,
          )
        }
      } catch (error) {
        if (!cancelled) {
          setHistoryError(
            error instanceof Error
              ? error.message
              : 'Unable to load investigation history.',
          )
        }
      } finally {
        if (!cancelled) {
          setHistoryLoading(false)
        }
      }
    }

    void loadInitialHistory()

    return () => {
      cancelled = true
    }
  }, [])


  // =========================
  // EventSource Cleanup
  // =========================

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close()
      eventSourceRef.current = null
    }
  }, [])


  // =========================
  // View Historical Run
  // =========================

  async function handleViewInvestigation(
    investigationId: string,
  ) {
    setHistoryDetailLoading(true)
    setHistoryDetailError(null)

    try {
      const investigation =
        await getInvestigationRun(
          investigationId,
        )

      setInvestigationResult(
        investigation,
      )

      // Historical investigations do not
      // have a live execution timeline.
      setStreamEvents([])

      setInvestigationError(null)
      setFailedIncidentId(null)

      // Scroll to the details after React
      // renders the investigation panel.
      window.setTimeout(() => {
        document
          .querySelector(
            '.investigation-panel',
          )
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          })
      }, 0)
    } catch (error) {
      setHistoryDetailError(
        error instanceof Error
          ? error.message
          : 'Unable to load investigation details.',
      )
    } finally {
      setHistoryDetailLoading(false)
    }
  }


  async function handleCompareInvestigations() {
    if (
      !baselineInvestigationId ||
      !comparisonInvestigationId
    ) {
      setComparisonError(
        'Select two investigation runs to compare.',
      )
      return
    }

    if (
      baselineInvestigationId ===
      comparisonInvestigationId
    ) {
      setComparisonError(
        'Select two different investigation runs.',
      )
      return
    }

    setComparisonLoading(true)
    setComparisonError(null)
    setInvestigationComparison(null)

    try {
      const comparison =
        await getInvestigationComparison(
          baselineInvestigationId,
          comparisonInvestigationId,
        )

      setInvestigationComparison(
        comparison,
      )

      window.setTimeout(() => {
        document
          .querySelector(
            '.investigation-comparison',
          )
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          })
      }, 0)
    } catch (error) {
      setComparisonError(
        error instanceof Error
          ? error.message
          : 'Unable to compare investigations.',
      )
    } finally {
      setComparisonLoading(false)
    }
  }


  // =========================
  // Start Investigation
  // =========================

  function handleInvestigate(
    incidentId: string,
  ) {
    // Close any previous investigation stream.
    eventSourceRef.current?.close()
    eventSourceRef.current = null

    // Reset the UI for the new investigation.
    setInvestigatingIncidentId(
      incidentId,
    )

    setInvestigationError(null)
    setFailedIncidentId(null)
    setInvestigationResult(null)
    setStreamEvents([])

    // Clear any previous historical-detail error.
    setHistoryDetailError(null)

    const eventSource = streamInvestigation(
      incidentId,

      (event) => {
        // =========================
        // Investigation Started
        // =========================

        if (event.event === 'started') {
          setStreamEvents(
            (current) => [
              ...current,
              event,
            ],
          )

          return
        }


        // =========================
        // Investigation Progress
        // =========================

        if (event.event === 'progress') {
          // Internal triage event is not
          // shown to the user.
          if (event.step === 'triage') {
            return
          }

          setStreamEvents(
            (current) => [
              ...current,
              event,
            ],
          )

          return
        }


        // =========================
        // Investigation Completed
        // =========================

        if (
          event.event === 'completed' &&
          event.data
        ) {
          setStreamEvents(
            (current) => [
              ...current,
              event,
            ],
          )

          setInvestigationResult(
            event.data,
          )

          setInvestigatingIncidentId(
            null,
          )

          eventSourceRef.current?.close()
          eventSourceRef.current = null

          /*
           * The backend persists the completed
           * investigation before emitting the
           * completed SSE event.
           *
           * Therefore the new investigation
           * should already exist when this
           * history request executes.
           */
          void refreshInvestigationHistory()

          return
        }


        // =========================
        // Backend Investigation Error
        // =========================

        if (
          event.event ===
          'investigation_error'
        ) {
          setInvestigationError(
            event.message,
          )

          setFailedIncidentId(
            incidentId,
          )

          setInvestigatingIncidentId(
            null,
          )

          eventSourceRef.current?.close()
          eventSourceRef.current = null
        }
      },


      // =========================
      // EventSource / Network Error
      // =========================

      (message) => {
        setInvestigationError(
          message,
        )

        setFailedIncidentId(
          incidentId,
        )

        setInvestigatingIncidentId(
          null,
        )

        eventSourceRef.current?.close()
        eventSourceRef.current = null
      },
    )

    eventSourceRef.current =
      eventSource
  }

  async function handleViewRCAReport(
  investigationId: string,
) {
  setRCAReportLoading(true)
  setRCAReportError(null)
  setSelectedRCAReport(null)

  try {
    const report =
      await getRCAReport(
        investigationId,
      )

    setSelectedRCAReport(report)
  } catch (error) {
    const message =
      error instanceof Error
        ? error.message
        : 'Unable to load the RCA report.'

    setRCAReportError(message)
  } finally {
    setRCAReportLoading(false)
  }
}

function handleCloseRCAReport() {
  setSelectedRCAReport(null)
  setRCAReportError(null)
}

  return (
    <div className="dashboard-page">
      <Header
        title="Production Incident Intelligence"
        description="Monitor active incidents, investigations, and root-cause analysis across production systems."
      />

      <div className="dashboard-content">

        {/* =========================
            System Overview
        ========================== */}

        <section className="overview-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                System Overview
              </p>

              <h2>
                Incident Operations
              </h2>
            </div>

            <span className="section-meta">
              Production environment
            </span>
          </div>

          <div className="stats-grid">
            {overviewStats.map(
              (stat) => (
                <StatCard
                  key={stat.label}
                  label={stat.label}
                  value={stat.value}
                  detail={stat.detail}
                  tone={stat.tone}
                />
              ),
            )}
          </div>
        </section>


        {/* =========================
            Incident Queue
        ========================== */}

        <section className="incidents-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                Incident Queue
              </p>

              <h2>
                Recent / Active Incidents
              </h2>
            </div>

            <span className="section-meta">
              1 active incident
            </span>
          </div>

          <IncidentTable
            incidents={incidents}
            investigatingIncidentId={
              investigatingIncidentId
            }
            onInvestigate={
              handleInvestigate
            }
          />


          {/* =========================
              Live Investigation
          ========================== */}

          {streamEvents.length > 0 && (
            <InvestigationTimeline
              incidentId={
                investigatingIncidentId ??
                investigationResult
                  ?.incident_id ??
                failedIncidentId ??
                'Unknown'
              }
              events={streamEvents}
            />
          )}
        </section>


        {/* =========================
            Investigation History
        ========================== */}

        <InvestigationHistory
          history={investigationHistory}
          loading={historyLoading}
          error={historyError}
          onViewInvestigation={
            handleViewInvestigation
          }
          onViewReport={
            handleViewRCAReport
          }
        />

        {rcaReportLoading && (
          <div className="rca-report-state">
            <div className="rca-report-spinner" />

            <div>
              <strong>
                Loading RCA Report
              </strong>

              <p>
                Retrieving the persisted
                investigation analysis...
              </p>
            </div>
          </div>
        )}

        {rcaReportError && (
          <div className="rca-report-state rca-report-state-error">
            <div>
              <strong>
                Unable to load RCA report
              </strong>

              <p>
                {rcaReportError}
              </p>
            </div>
          </div>
        )}

        {selectedRCAReport && (
          <RCAReportView
            report={selectedRCAReport}
            onClose={
              handleCloseRCAReport
            }
          />
        )}



        {investigationHistory.length >= 2 && (
          <section className="comparison-selector">
            <div className="comparison-selector-header">
              <div>
                <p className="eyebrow">
                  Run Comparison
                </p>

                <h2>
                  Compare Investigations
                </h2>

                <p className="comparison-selector-description">
                  Compare two persisted investigation runs
                  to see how evidence, hypotheses, confidence,
                  and execution changed.
                </p>
              </div>
            </div>

            <div className="comparison-selector-controls">
              <div className="comparison-field">
                <label htmlFor="baseline-investigation">
                  Baseline
                </label>

                <select
                  id="baseline-investigation"
                  value={baselineInvestigationId}
                  onChange={(event) => {
                    setBaselineInvestigationId(
                      event.target.value,
                    )

                    setInvestigationComparison(null)
                    setComparisonError(null)
                  }}
                >
                  <option value="">
                    Select baseline run
                  </option>

                  {investigationHistory.map((item) => (
                    <option
                      key={item.investigation_id}
                      value={item.investigation_id}
                    >
                      {item.investigation_id}
                    </option>
                  ))}
                </select>
              </div>

              <div
                className="comparison-direction"
                aria-hidden="true"
              >
                →
              </div>

              <div className="comparison-field">
                <label htmlFor="comparison-investigation">
                  Comparison
                </label>

                <select
                  id="comparison-investigation"
                  value={comparisonInvestigationId}
                  onChange={(event) => {
                    setComparisonInvestigationId(
                      event.target.value,
                    )

                    setInvestigationComparison(null)
                    setComparisonError(null)
                  }}
                >
                  <option value="">
                    Select comparison run
                  </option>

                  {investigationHistory.map((item) => (
                    <option
                      key={item.investigation_id}
                      value={item.investigation_id}
                    >
                      {item.investigation_id}
                    </option>
                  ))}
                </select>
              </div>

              <button
                type="button"
                className="comparison-button"
                disabled={
                  comparisonLoading ||
                  !baselineInvestigationId ||
                  !comparisonInvestigationId ||
                  baselineInvestigationId ===
                    comparisonInvestigationId
                }
                onClick={() => {
                  void handleCompareInvestigations()
                }}
              >
                {comparisonLoading
                  ? 'Comparing...'
                  : 'Compare Runs'}
              </button>
            </div>

            {comparisonError && (
              <div className="comparison-error">
                {comparisonError}
              </div>
            )}
          </section>
        )}


        {investigationComparison && (
         <InvestigationComparison
            history={investigationHistory}
            baselineId={baselineInvestigationId}
            comparisonId={comparisonInvestigationId}
            comparison={investigationComparison}
            loading={comparisonLoading}
            error={comparisonError}
            onBaselineChange={setBaselineInvestigationId}
            onComparisonChange={setComparisonInvestigationId}
            onCompare={handleCompareInvestigations}
          />
        )}


        {/* =========================
            Historical Detail State
        ========================== */}

        {historyDetailLoading && (
          <div className="history-detail-state">
            Loading investigation details...
          </div>
        )}

        {historyDetailError && (
          <div className="history-detail-state history-detail-state-error">
            {historyDetailError}
          </div>
        )}


        {/* =========================
            Investigation Error
        ========================== */}

        {investigationError &&
          failedIncidentId && (
            <InvestigationError
              message={
                investigationError
              }
              incidentId={
                failedIncidentId
              }
              onRetry={() =>
                handleInvestigate(
                  failedIncidentId,
                )
              }
            />
          )}


        {/* =========================
            Investigation Result
        ========================== */}

        {investigationResult && (
          <InvestigationPanel
            investigation={
              investigationResult
            }
          />
        )}
      </div>
    </div>
  )
}


export default DashboardPage