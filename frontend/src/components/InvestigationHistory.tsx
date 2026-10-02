import type { InvestigationHistoryItem } from '../types/investigation'

type InvestigationHistoryProps = {
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
            ◷
          </div>

          <div>
            <h2>
              Investigation History
            </h2>

            <p>
              Previous investigations for INC-001
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
                    ▣
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
                        ↻ {item.iteration}{' '}
                        {item.iteration === 1
                          ? 'iteration'
                          : 'iterations'}
                      </span>

                      <span>
                        ☷ Step:{' '}
                        {item.current_step}
                      </span>

                      <span>
                        ◇ {item.incident_id}
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
                      →
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