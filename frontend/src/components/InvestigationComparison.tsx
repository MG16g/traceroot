import type {
  InvestigationComparisonResponse,
  InvestigationHistoryItem,
} from '../types/investigation'

type InvestigationComparisonProps = {
  history: InvestigationHistoryItem[]
  baselineId: string
  comparisonId: string
  comparison: InvestigationComparisonResponse | null
  loading: boolean
  error: string | null
  onBaselineChange: (investigationId: string) => void
  onComparisonChange: (investigationId: string) => void
  onCompare: () => void
}

function formatDate(timestamp: string) {
  const date = new Date(timestamp)

  if (Number.isNaN(date.getTime())) {
    return timestamp
  }

  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

function formatConfidence(
  confidence: number | null,
) {
  if (confidence === null) {
    return 'No RCA'
  }

  return `${Math.round(confidence * 100)}%`
}

function formatDelta(
  value: number | null,
  percentage = false,
) {
  if (value === null) {
    return 'N/A'
  }

  const formattedValue = percentage
    ? Math.round(value * 100)
    : value

  if (formattedValue > 0) {
    return `+${formattedValue}${percentage ? '%' : ''}`
  }

  return `${formattedValue}${percentage ? '%' : ''}`
}

function deltaClass(
  value: number | null,
) {
  if (value === null || value === 0) {
    return 'comparison-delta-neutral'
  }

  if (value > 0) {
    return 'comparison-delta-positive'
  }

  return 'comparison-delta-negative'
}

function statusClass(status: string | null) {
  if (!status) {
    return 'comparison-status-neutral'
  }

  const normalized = status.toLowerCase()

  if (
    normalized === 'supported' ||
    normalized === 'completed'
  ) {
    return 'comparison-status-success'
  }

  if (
    normalized === 'failed' ||
    normalized === 'rejected'
  ) {
    return 'comparison-status-danger'
  }

  return 'comparison-status-warning'
}

type EvolutionRowProps = {
  label: string
  baseline: string | number
  comparison: string | number
  delta: number | null
  percentage?: boolean
}

function EvolutionRow({
  label,
  baseline,
  comparison,
  delta,
  percentage = false,
}: EvolutionRowProps) {
  return (
    <div className="comparison-evolution-row">
      <span className="comparison-evolution-label">
        {label}
      </span>

      <strong className="comparison-evolution-value">
        {baseline}
      </strong>

      <div
        className="comparison-evolution-arrow"
        aria-hidden="true"
      >
        <span />
        <span>→</span>
      </div>

      <strong className="comparison-evolution-value">
        {comparison}
      </strong>

      <strong
        className={`comparison-evolution-delta ${deltaClass(
          delta,
        )}`}
      >
        {formatDelta(delta, percentage)}
      </strong>
    </div>
  )
}

function InvestigationComparison({
  history,
  baselineId,
  comparisonId,
  comparison,
  loading,
  error,
  onBaselineChange,
  onComparisonChange,
  onCompare,
}: InvestigationComparisonProps) {
  const canCompare =
    baselineId.length > 0 &&
    comparisonId.length > 0 &&
    baselineId !== comparisonId &&
    !loading

  return (
    <section className="comparison-panel">
      <div className="comparison-panel-header">
        <div className="comparison-heading-group">
          <div
            className="comparison-heading-icon"
            aria-hidden="true"
          >
            ⇄
          </div>

          <div>
            <h2>Investigation Comparison</h2>

            <p>
              Compare how the RCA evolved between
              historical investigation runs.
            </p>
          </div>
        </div>

        {comparison && (
          <span className="comparison-ready-badge">
            <span
              className="comparison-ready-dot"
              aria-hidden="true"
            />
            Comparison ready
          </span>
        )}
      </div>

      <div className="comparison-selector-card">
        <div className="comparison-selector-grid">
          <div className="comparison-selector">
            <label htmlFor="baseline-investigation">
              Baseline Run
            </label>

            <select
              id="baseline-investigation"
              value={baselineId}
              onChange={(event) =>
                onBaselineChange(
                  event.target.value,
                )
              }
            >
              <option value="">
                Select baseline investigation
              </option>

              {history.map((item) => (
                <option
                  key={item.investigation_id}
                  value={item.investigation_id}
                >
                  {item.investigation_id} ·{' '}
                  {formatDate(item.created_at)}
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

          <div className="comparison-selector">
            <label htmlFor="comparison-investigation">
              Comparison Run
            </label>

            <select
              id="comparison-investigation"
              value={comparisonId}
              onChange={(event) =>
                onComparisonChange(
                  event.target.value,
                )
              }
            >
              <option value="">
                Select comparison investigation
              </option>

              {history.map((item) => (
                <option
                  key={item.investigation_id}
                  value={item.investigation_id}
                >
                  {item.investigation_id} ·{' '}
                  {formatDate(item.created_at)}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            className="comparison-button"
            disabled={!canCompare}
            onClick={onCompare}
          >
            {loading
              ? 'Comparing...'
              : 'Compare Runs'}
          </button>
        </div>
      </div>

      {baselineId &&
        comparisonId &&
        baselineId === comparisonId && (
          <div className="comparison-state comparison-state-warning">
            Select two different investigation runs.
          </div>
        )}

      {error && (
        <div className="comparison-state comparison-state-error">
          {error}
        </div>
      )}

      {!error && loading && (
        <div className="comparison-state">
          <span className="comparison-loading-spinner" />
          Comparing investigation runs...
        </div>
      )}

      {!loading &&
        !error &&
        !comparison && (
          <div className="comparison-empty-state">
            <div
              className="comparison-empty-icon"
              aria-hidden="true"
            >
              ⇄
            </div>

            <strong>
              Select two investigation runs
            </strong>

            <span>
              TraceRoot will compare their RCA confidence,
              iterations, actions, evidence and hypotheses.
            </span>
          </div>
        )}

      {!loading &&
        !error &&
        comparison && (
          <>
            <div className="comparison-runs-grid">
              <article className="comparison-run-card">
                <div className="comparison-run-card-header">
                  <div>
                    <span className="comparison-run-label">
                      Baseline
                    </span>

                    <strong>
                      {
                        comparison.baseline
                          .investigation_id
                      }
                    </strong>
                  </div>

                  <span
                    className={`comparison-run-status ${statusClass(
                      comparison.baseline.status,
                    )}`}
                  >
                    {comparison.baseline.status}
                  </span>
                </div>

                <span className="comparison-run-date">
                  {formatDate(
                    comparison.baseline.created_at,
                  )}
                </span>

                <div className="comparison-confidence">
                  <div>
                    <span>RCA Confidence</span>
                    <small>
                      Root cause certainty
                    </small>
                  </div>

                  <strong>
                    {formatConfidence(
                      comparison.baseline
                        .root_cause_confidence,
                    )}
                  </strong>
                </div>

                <div className="comparison-metrics">
                  <div>
                    <span>Iterations</span>
                    <strong>
                      {comparison.baseline.iteration}
                    </strong>
                  </div>

                  <div>
                    <span>Actions</span>
                    <strong>
                      {
                        comparison.baseline
                          .action_count
                      }
                    </strong>
                  </div>

                  <div>
                    <span>Evidence</span>
                    <strong>
                      {
                        comparison.baseline
                          .evidence_count
                      }
                    </strong>
                  </div>

                  <div>
                    <span>Hypotheses</span>
                    <strong>
                      {
                        comparison.baseline
                          .hypothesis_count
                      }
                    </strong>
                  </div>
                </div>

                <div className="comparison-root-status">
                  <span>Root Cause Status</span>

                  <strong
                    className={statusClass(
                      comparison.baseline
                        .root_cause_status,
                    )}
                  >
                    {comparison.baseline
                      .root_cause_status ?? 'No RCA'}
                  </strong>
                </div>
              </article>

              <div
                className="comparison-between-runs"
                aria-hidden="true"
              >
                <span>→</span>
              </div>

              <article className="comparison-run-card comparison-run-card-current">
                <div className="comparison-run-card-header">
                  <div>
                    <span className="comparison-run-label">
                      Comparison
                    </span>

                    <strong>
                      {
                        comparison.comparison
                          .investigation_id
                      }
                    </strong>
                  </div>

                  <span
                    className={`comparison-run-status ${statusClass(
                      comparison.comparison.status,
                    )}`}
                  >
                    {comparison.comparison.status}
                  </span>
                </div>

                <span className="comparison-run-date">
                  {formatDate(
                    comparison.comparison.created_at,
                  )}
                </span>

                <div className="comparison-confidence">
                  <div>
                    <span>RCA Confidence</span>
                    <small>
                      Root cause certainty
                    </small>
                  </div>

                  <strong>
                    {formatConfidence(
                      comparison.comparison
                        .root_cause_confidence,
                    )}
                  </strong>
                </div>

                <div className="comparison-metrics">
                  <div>
                    <span>Iterations</span>
                    <strong>
                      {comparison.comparison.iteration}
                    </strong>
                  </div>

                  <div>
                    <span>Actions</span>
                    <strong>
                      {
                        comparison.comparison
                          .action_count
                      }
                    </strong>
                  </div>

                  <div>
                    <span>Evidence</span>
                    <strong>
                      {
                        comparison.comparison
                          .evidence_count
                      }
                    </strong>
                  </div>

                  <div>
                    <span>Hypotheses</span>
                    <strong>
                      {
                        comparison.comparison
                          .hypothesis_count
                      }
                    </strong>
                  </div>
                </div>

                <div className="comparison-root-status">
                  <span>Root Cause Status</span>

                  <strong
                    className={statusClass(
                      comparison.comparison
                        .root_cause_status,
                    )}
                  >
                    {comparison.comparison
                      .root_cause_status ?? 'No RCA'}
                  </strong>
                </div>
              </article>
            </div>

            <div className="comparison-change-section">
              <div className="comparison-change-heading">
                <div>
                  <span className="comparison-section-label">
                    Change Summary
                  </span>

                  <h3>
                    Investigation evolution
                  </h3>

                  <p>
                    How the investigation changed from
                    the baseline run to the comparison run.
                  </p>
                </div>

                <span className="comparison-incident">
                  {
                    comparison.baseline
                      .incident_id
                  }
                </span>
              </div>

              <div className="comparison-evolution-table">
                <div className="comparison-evolution-header">
                  <span>Metric</span>
                  <span>Baseline</span>
                  <span />
                  <span>Comparison</span>
                  <span>Change</span>
                </div>

                <EvolutionRow
                  label="RCA Confidence"
                  baseline={formatConfidence(
                    comparison.baseline
                      .root_cause_confidence,
                  )}
                  comparison={formatConfidence(
                    comparison.comparison
                      .root_cause_confidence,
                  )}
                  delta={
                    comparison.changes
                      .confidence_delta
                  }
                  percentage
                />

                <EvolutionRow
                  label="Iterations"
                  baseline={
                    comparison.baseline.iteration
                  }
                  comparison={
                    comparison.comparison.iteration
                  }
                  delta={
                    comparison.changes
                      .iteration_delta
                  }
                />

                <EvolutionRow
                  label="Actions"
                  baseline={
                    comparison.baseline
                      .action_count
                  }
                  comparison={
                    comparison.comparison
                      .action_count
                  }
                  delta={
                    comparison.changes
                      .action_count_delta
                  }
                />

                <EvolutionRow
                  label="Evidence"
                  baseline={
                    comparison.baseline
                      .evidence_count
                  }
                  comparison={
                    comparison.comparison
                      .evidence_count
                  }
                  delta={
                    comparison.changes
                      .evidence_count_delta
                  }
                />

                <EvolutionRow
                  label="Hypotheses"
                  baseline={
                    comparison.baseline
                      .hypothesis_count
                  }
                  comparison={
                    comparison.comparison
                      .hypothesis_count
                  }
                  delta={
                    comparison.changes
                      .hypothesis_count_delta
                  }
                />
              </div>

              <div className="comparison-detail-heading">
                <div>
                  <span className="comparison-section-label">
                    Investigation Changes
                  </span>

                  <h3>Run differences</h3>
                </div>
              </div>

              <div className="comparison-change-details">
                <div>
                  <span>New Evidence</span>
                  <strong>
                    {
                      comparison.changes
                        .new_evidence_count
                    }
                  </strong>
                </div>

                <div>
                  <span>Removed Evidence</span>
                  <strong>
                    {
                      comparison.changes
                        .removed_evidence_count
                    }
                  </strong>
                </div>

                <div>
                  <span>New Hypotheses</span>
                  <strong>
                    {
                      comparison.changes
                        .new_hypothesis_count
                    }
                  </strong>
                </div>

                <div>
                  <span>Removed Hypotheses</span>
                  <strong>
                    {
                      comparison.changes
                        .removed_hypothesis_count
                    }
                  </strong>
                </div>

                <div>
                  <span>Status Changed</span>

                  <strong>
                    {comparison.changes.status_changed
                      ? 'Yes'
                      : 'No'}
                  </strong>
                </div>

                <div>
                  <span>RCA Status Changed</span>

                  <strong>
                    {comparison.changes
                      .root_cause_status_changed
                      ? 'Yes'
                      : 'No'}
                  </strong>
                </div>
              </div>

              <div className="comparison-status-transition">
                <div>
                  <span>RCA Status Evolution</span>

                  <div className="comparison-status-flow">
                    <strong
                      className={statusClass(
                        comparison.baseline
                          .root_cause_status,
                      )}
                    >
                      {comparison.baseline
                        .root_cause_status ?? 'No RCA'}
                    </strong>

                    <span aria-hidden="true">
                      →
                    </span>

                    <strong
                      className={statusClass(
                        comparison.comparison
                          .root_cause_status,
                      )}
                    >
                      {comparison.comparison
                        .root_cause_status ?? 'No RCA'}
                    </strong>
                  </div>
                </div>

                <span
                  className={`comparison-status-change-badge ${
                    comparison.changes
                      .root_cause_status_changed
                      ? 'comparison-status-change-yes'
                      : 'comparison-status-change-no'
                  }`}
                >
                  {comparison.changes
                    .root_cause_status_changed
                    ? 'Status changed'
                    : 'No status change'}
                </span>
              </div>
            </div>
          </>
        )}
    </section>
  )
}

export default InvestigationComparison