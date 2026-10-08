import type { RCAReportSummary } from '../types/investigation'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

type RCAReportViewProps = {
  report: RCAReportSummary
  onClose?: () => void
}

function formatReportDate(
  timestamp: string,
) {
  const date = new Date(timestamp)

  if (Number.isNaN(date.getTime())) {
    return timestamp
  }

  return date.toLocaleString()
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

function formatAction(
  action: string,
) {
  const [name, parameters] =
    action.split('|', 2)

  return {
    name: name
      .replaceAll('_', ' ')
      .replace(/\b\w/g, (character) =>
        character.toUpperCase(),
      ),
    parameters:
      parameters ?? null,
  }
}

function RCAReportView({
  report,
  onClose,
}: RCAReportViewProps) {
  const confidence =
    confidencePercentage(
      report.root_cause_confidence,
    )

  const rootCauseStatus =
    report.root_cause_status ??
    'No RCA'

  const supported =
    rootCauseStatus.toLowerCase() ===
    'supported'

  const investigating =
    rootCauseStatus.toLowerCase() ===
    'investigating'

  return (
    <section className="rca-report-view">
      <div className="rca-report-header">
        <div>
          <p className="eyebrow">
            Root Cause Analysis
          </p>

          <h2>
            RCA Report
          </h2>

          <div className="rca-report-identifiers">
            <code>
              {report.investigation_id}
            </code>

            <span>•</span>

            <strong>
              {report.incident_id}
            </strong>

            <span>•</span>

            <span>
              {formatReportDate(
                report.created_at,
              )}
            </span>
          </div>
        </div>

        {onClose && (
          <button
            type="button"
            className="rca-report-close"
            onClick={onClose}
            aria-label="Close RCA report"
            title="Close RCA report"
          >
            ×
          </button>
        )}
      </div>

      <div className="rca-root-cause-card">
        <div className="rca-root-cause-copy">
          <span className="rca-section-label">
            Determined Root Cause
          </span>

          <h3>
            {report.root_cause_description ??
              'No root cause has been established.'}
          </h3>

          <div className="rca-root-cause-meta">
            <span
              className={`rca-status-badge ${
                supported
                  ? 'rca-status-supported'
                  : investigating
                    ? 'rca-status-investigating'
                    : 'rca-status-neutral'
              }`}
            >
              {rootCauseStatus}
            </span>

            {report.source_types.length > 0 && (
              <span className="rca-source-summary">
                Sources:{' '}
                {report.source_types.join(
                  ', ',
                )}
              </span>
            )}
          </div>
        </div>

        <div className="rca-confidence">
          <span>
            RCA Confidence
          </span>

          <strong>
            {confidence !== null
              ? `${confidence}%`
              : '—'}
          </strong>
        </div>
      </div>

      <div className="rca-metrics-grid">
        <article className="rca-metric">
          <span>Iterations</span>
          <strong>
            {report.iteration}
          </strong>
        </article>

        <article className="rca-metric">
          <span>Evidence</span>
          <strong>
            {report.evidence_count}
          </strong>
        </article>

        <article className="rca-metric">
          <span>Hypotheses</span>
          <strong>
            {report.hypothesis_count}
          </strong>
        </article>

        <article className="rca-metric">
          <span>Actions</span>
          <strong>
            {report.action_count}
          </strong>
        </article>
      </div>

      <div className="rca-report-grid">
        <article className="rca-report-section">
          <div className="rca-section-heading">
            <h3>
              Supporting Evidence
            </h3>

            <span>
              {
                report
                  .supporting_evidence
                  .length
              }
            </span>
          </div>

          {report.supporting_evidence
            .length > 0 ? (
            <ul className="rca-reference-list">
              {report.supporting_evidence.map(
                (item, index) => (
                  <li
                    key={`${item}-${index}`}
                  >
                    {item}
                  </li>
                ),
              )}
            </ul>
          ) : (
            <p className="rca-empty-copy">
              No supporting evidence
              references were recorded.
            </p>
          )}
        </article>

        <article className="rca-report-section">
          <div className="rca-section-heading">
            <h3>
              Contradicting Evidence
            </h3>

            <span>
              {
                report
                  .contradicting_evidence
                  .length
              }
            </span>
          </div>

          {report.contradicting_evidence
            .length > 0 ? (
            <ul className="rca-reference-list">
              {report.contradicting_evidence.map(
                (item, index) => (
                  <li
                    key={`${item}-${index}`}
                  >
                    {item}
                  </li>
                ),
              )}
            </ul>
          ) : (
            <p className="rca-empty-copy">
              No contradicting evidence
              was identified.
            </p>
          )}
        </article>
      </div>

      <article className="rca-report-section rca-evidence-section">
        <div className="rca-section-heading">
          <h3>
            Collected Evidence
          </h3>

          <span>
            {report.evidence.length}
          </span>
        </div>

        {report.evidence.length > 0 ? (
          <div className="rca-evidence-list">
            {report.evidence.map(
              (evidence) => (
                <div
                  key={evidence.id}
                  className="rca-evidence-item"
                >
                  <div className="rca-evidence-header">
                    <div>
                      <strong>
                        {evidence.id}
                      </strong>

                      <span>
                        {evidence.source_type}
                      </span>
                    </div>

                    <code>
                      {evidence.service}
                    </code>
                  </div>

                  <p>
                    {evidence.content}
                  </p>

                  <span className="rca-relevance">
                    Relevance:{' '}
                    {Math.round(
                      evidence.relevance_score *
                        100,
                    )}
                    %
                  </span>
                </div>
              ),
            )}
          </div>
        ) : (
          <p className="rca-empty-copy">
            No evidence was persisted for
            this investigation.
          </p>
        )}
      </article>

      <article className="rca-report-section">
        <div className="rca-section-heading">
          <h3>
            Investigation Actions
          </h3>

          <span>
            {
              report.executed_actions
                .length
            }
          </span>
        </div>

        {report.executed_actions.length >
        0 ? (
          <ol className="rca-action-list">
            {report.executed_actions.map(
              (action, index) => {
                const formatted =
                  formatAction(action)

                return (
                  <li
                    key={`${action}-${index}`}
                  >
                    <div className="rca-action-number">
                      {index + 1}
                    </div>

                    <div className="rca-action-content">
                      <strong>
                        {formatted.name}
                      </strong>

                      {formatted.parameters && (
                        <code>
                          {
                            formatted.parameters
                          }
                        </code>
                      )}
                    </div>
                  </li>
                )
              },
            )}
          </ol>
        ) : (
          <p className="rca-empty-copy">
            No investigation actions were
            recorded.
          </p>
        )}
      </article>

      <article className="rca-detailed-report">
        <div className="rca-section-heading">
          <div>
            <span className="rca-section-label">
              Generated Analysis
            </span>

            <h3>
              Detailed RCA Report
            </h3>
          </div>

          <span className="rca-report-status">
            {report.investigation_status}
          </span>
        </div>

        {report.final_report ? (
          <div className="rca-report-content rca-markdown">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {report.final_report}
            </ReactMarkdown>
          </div>
        ) : (
          <p className="rca-empty-copy">
            No detailed RCA report was
            generated for this run.
          </p>
        )}
      </article>

      {report.error && (
        <div className="rca-report-error">
          <strong>
            Investigation Error
          </strong>

          <p>
            {report.error}
          </p>
        </div>
      )}
    </section>
  )
}

export default RCAReportView