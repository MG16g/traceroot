import type { InvestigationHistoryItem } from '../types/investigation'

type InvestigationHistoryProps = {
  incidentId: string
  history: InvestigationHistoryItem[]
  loading: boolean
  error: string | null

  onViewInvestigation: (
    investigationId: string,
  ) => void

  onViewReport: (
    investigationId: string,
  ) => void
}


function formatHistoryDate(timestamp: string) {
  const date = new Date(timestamp)

  if (Number.isNaN(date.getTime())) {
    return {
      date: timestamp,
      time: '',
    }
  }

  return {
    date: date.toLocaleDateString(
      undefined,
      {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      },
    ),
    time: date.toLocaleTimeString(
      undefined,
      {
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
      },
    ),
  }
}

function confidencePercentage(
  confidence: number | null,
) {
  if (confidence === null) {
    return null
  }

  return Math.round(
    confidence * 100,
  )
}

function InvestigationHistory({
  incidentId,
  history,
  loading,
  error,
  onViewInvestigation,
  onViewReport,
}: InvestigationHistoryProps) {
  return (
    <section className="history-panel">
      <div className="history-panel-header">
        <div className="history-heading-group">
          <div
            className="history-heading-icon"
            aria-hidden="true"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M3 12a9 9 0 1 0 3-6.7" />
              <path d="M3 3v6h6" />
              <path d="M12 7v5l3 2" />
            </svg>
          </div>

          <div>
            <h2>
              Investigation History
            </h2>

            <p>
              Previous investigations for {incidentId}
            </p>
          </div>
        </div>

        {!loading && !error && (
          <span className="history-count">
            {history.length}{' '}
            {history.length === 1
              ? 'investigation'
              : 'investigations'}
          </span>
        )}
      </div>

      {loading && (
        <div className="history-state">
          Loading investigation history...
        </div>
      )}

      {!loading && error && (
        <div className="history-state history-state-error">
          {error}
        </div>
      )}

      {!loading &&
        !error &&
        history.length === 0 && (
          <div className="history-state">
            No previous investigations yet.
          </div>
        )}

      {!loading &&
        !error &&
        history.length > 0 && (
          <div className="history-rows">
            {history.map((item) => {
              const timestamp =
                formatHistoryDate(
                  item.created_at,
                )

              const confidence =
                confidencePercentage(
                  item.root_cause_confidence,
                )

              const successful =
                item.status.toLowerCase() !==
                'failed'

              return (
                <article
                  key={item.investigation_id}
                  className="history-row"
                >
                  <div
                    className="history-calendar"
                    aria-hidden="true"
                  >
                    <svg
                      width="19"
                      height="19"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <rect x="3" y="5" width="18" height="16" rx="2" />
                      <path d="M7 3v4M17 3v4M3 10h18" />
                    </svg>
                  </div>

                  <div className="history-time">
                    <strong>
                      {timestamp.date}
                    </strong>

                    <span>
                      {timestamp.time}
                    </span>
                  </div>

                  <div className="history-run">
                    <div className="history-run-heading">
                      <strong className="history-run-id">
                        {item.investigation_id}
                      </strong>

                      <span
                        className={`history-run-status ${
                          successful
                            ? 'history-run-success'
                            : 'history-run-failed'
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>

                    <div className="history-run-meta">
                      <span>
                        {item.iteration}{' '}
                        {item.iteration === 1 ? 'iteration' : 'iterations'}
                      </span>

                      <span>
                        Step: {item.current_step}
                      </span>

                      <span>
                        {item.incident_id}
                      </span>
                    </div>
                  </div>

                  <div className="history-rca">
                    <div
                      className={`confidence-ring ${
                        confidence === null
                          ? 'confidence-ring-empty'
                          : ''
                      }`}
                      style={
                        confidence !== null
                          ? {
                              '--confidence':
                                `${confidence * 3.6}deg`,
                            } as React.CSSProperties
                          : undefined
                      }
                    >
                      <div className="confidence-ring-inner">
                        {confidence !== null
                          ? `${confidence}%`
                          : '—'}
                      </div>
                    </div>

                    <div className="history-confidence-copy">
                      <span>
                        RCA Confidence
                      </span>

                      <strong>
                        {confidence !== null
                          ? `${confidence}%`
                          : 'No RCA'}
                      </strong>
                    </div>
                  </div>

                  <div className="history-actions">
                    <button
                      type="button"
                      className="history-report-button"
                      onClick={() =>
                        onViewReport(
                          item.investigation_id,
                        )
                      }
                      title={`View RCA report for ${item.investigation_id}`}
                    >
                      RCA Report
                    </button>

                    <button
                      type="button"
                      className="history-details-button"
                      aria-label={`View investigation ${item.investigation_id}`}
                      title="View investigation details"
                      onClick={() =>
                        onViewInvestigation(
                          item.investigation_id,
                        )
                      }
                    >
                      <svg
                        width="17"
                        height="17"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M5 12h14M13 6l6 6-6 6" />
                      </svg>
                    </button>
                  </div>
                </article>
              )
            })}
          </div>
        )}
    </section>
  )
}

export default InvestigationHistory