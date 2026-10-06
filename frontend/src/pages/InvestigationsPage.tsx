import {
  useEffect,
  useRef,
  useState,
} from 'react'

import {
  useNavigate,
  useSearchParams,
} from 'react-router-dom'

import Header from '../components/Header'
import InvestigationComparison from '../components/InvestigationComparison'
import InvestigationError from '../components/InvestigationError'
import InvestigationHistory from '../components/InvestigationHistory'
import InvestigationPanel from '../components/InvestigationPanel'
import InvestigationTimeline from '../components/InvestigationTimeline'

import {
  getInvestigationComparison,
  getInvestigationHistory,
  getInvestigationRun,
  streamInvestigation,
} from '../services/investigationService'

import type {
  InvestigationComparisonResponse,
  InvestigationHistoryItem,
  InvestigationResponse,
  InvestigationStreamEvent,
} from '../types/investigation'

function InvestigationsPage() {

  const navigate = useNavigate()

  const [searchParams] = useSearchParams()

  const requestedIncidentId =
    searchParams.get('incident')

  // =========================
  // Investigation State
  // =========================

  const [
    investigatingIncidentId,
    setInvestigatingIncidentId,
  ] = useState<string | null>(null)

  const [
    investigationResult,
    setInvestigationResult,
  ] = useState<InvestigationResponse | null>(
    null,
  )

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

  // =========================
  // Investigation History
  // =========================

  const [
    investigationHistory,
    setInvestigationHistory,
  ] = useState<InvestigationHistoryItem[]>([])

  const [
    historyLoading,
    setHistoryLoading,
  ] = useState(false)

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

  // =========================
  // Investigation Comparison
  // =========================

  const [
    baselineInvestigationId,
    setBaselineInvestigationId,
  ] = useState('')

  const [
    comparisonInvestigationId,
    setComparisonInvestigationId,
  ] = useState('')

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

  // =========================
  // EventSource Reference
  // =========================

  const eventSourceRef =
    useRef<EventSource | null>(null)

  // =========================
  // Refresh Investigation History
  // =========================

  async function refreshInvestigationHistory(
    incidentId: string,
    showLoading = false,
  ) {
    if (showLoading) {
      setHistoryLoading(true)
    }

    setHistoryError(null)

    try {
      const history =
        await getInvestigationHistory(
          incidentId,
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
    if (!requestedIncidentId) {
      return
    }

    let cancelled = false

    async function loadHistory() {
      setHistoryLoading(true)
      setHistoryError(null)

      try {
        const history =
          await getInvestigationHistory(
            requestedIncidentId!,
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

    void loadHistory()

    return () => {
      cancelled = true
    }
  }, [requestedIncidentId])

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

  // =========================
  // Compare Investigations
  // =========================

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
            '.comparison-panel',
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

          void refreshInvestigationHistory(
            incidentId,
          )

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

  return (
    <div className="dashboard-page">
      <Header
        title="Investigations"
        description="Investigate incidents using telemetry evidence, hypothesis evaluation, and root-cause analysis."
      />

      <div className="dashboard-content">
        {/* =========================
            Investigation Workspace
        ========================== */}

        {requestedIncidentId && (
          <section className="incidents-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">
                  Investigation Workspace
                </p>

                <h2>
                  {requestedIncidentId}
                </h2>
              </div>

              <button
                type="button"
                className="investigate-button"
                disabled={
                  investigatingIncidentId !==
                  null
                }
                onClick={() =>
                  handleInvestigate(
                    requestedIncidentId,
                  )
                }
              >
                {investigatingIncidentId
                  ? 'Investigating...'
                  : 'Start Investigation'}
              </button>
            </div>

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
                  requestedIncidentId
                }
                events={streamEvents}
              />
            )}
          </section>
        )}

        {/* =========================
            No Incident Selected
        ========================== */}

        {!requestedIncidentId && (
          <section className="incidents-section">
            <div className="section-heading">
              <div>
                <p className="eyebrow">
                  Investigation Workspace
                </p>

                <h2>
                  Investigations
                </h2>

                <p>
                  Select an incident from the
                  Incidents page to start a new
                  investigation.
                </p>
              </div>
            </div>
          </section>
        )}

        {/* =========================
            Investigation History
        ========================== */}

        {requestedIncidentId && (
          <InvestigationHistory
            incidentId={requestedIncidentId}
            history={investigationHistory}
            loading={historyLoading}
            error={historyError}
            onViewInvestigation={
              handleViewInvestigation
            }
           onViewReport={(investigationId) => {
              navigate(
                `/rca-reports?incident=${encodeURIComponent(
                  requestedIncidentId,
                )}&investigation=${encodeURIComponent(
                  investigationId,
                )}`,
              )
            }}
          />
        )}

        {/* =========================
            Investigation Comparison
        ========================== */}

        {requestedIncidentId &&
          !historyLoading &&
          !historyError &&
          investigationHistory.length >= 2 && (
            <InvestigationComparison
              history={investigationHistory}
              baselineId={
                baselineInvestigationId
              }
              comparisonId={
                comparisonInvestigationId
              }
              comparison={
                investigationComparison
              }
              loading={
                comparisonLoading
              }
              error={
                comparisonError
              }
              onBaselineChange={(
                investigationId,
              ) => {
                setBaselineInvestigationId(
                  investigationId,
                )

                setInvestigationComparison(
                  null,
                )

                setComparisonError(null)
              }}
              onComparisonChange={(
                investigationId,
              ) => {
                setComparisonInvestigationId(
                  investigationId,
                )

                setInvestigationComparison(
                  null,
                )

                setComparisonError(null)
              }}
              onCompare={() => {
                void handleCompareInvestigations()
              }}
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

export default InvestigationsPage