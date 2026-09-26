import type { RootCauseResponse } from '../types/investigation'

type RootCausePanelProps = {
  rootCause: RootCauseResponse | null
}

function normalizeConfidence(confidence: number) {
  const normalized =
    confidence <= 1 ? confidence * 100 : confidence

  return Math.max(0, Math.min(100, Math.round(normalized)))
}

function RootCausePanel({
  rootCause,
}: RootCausePanelProps) {
  if (!rootCause) {
    return (
      <section className="reasoning-section">
        <div className="reasoning-section-header">
          <div>
            <p className="eyebrow">Deterministic Evaluation</p>
            <h3>Root Cause</h3>
          </div>
        </div>

        <div className="root-cause-empty">
          No supported root cause was produced for this investigation.
        </div>
      </section>
    )
  }

  const confidence = normalizeConfidence(rootCause.confidence)
  const statusClass = rootCause.status.toLowerCase()

  return (
    <section className="reasoning-section">
      <div className="reasoning-section-header">
        <div>
          <p className="eyebrow">Deterministic Evaluation</p>
          <h3>Root Cause</h3>
        </div>

        <span
          className={`root-cause-status root-cause-status-${statusClass}`}
        >
          {rootCause.status}
        </span>
      </div>

      <article className="root-cause-card">
        <div className="root-cause-header">
          <div>
            <span className="root-cause-label">
              Evidence-supported conclusion
            </span>

            <p className="root-cause-description">
              {rootCause.description}
            </p>
          </div>

          <div className="root-cause-confidence">
            <span>Confidence</span>
            <strong>{confidence}%</strong>
          </div>
        </div>

        <div className="confidence-track">
          <div
            className="confidence-fill root-cause-confidence-fill"
            style={{ width: `${confidence}%` }}
          />
        </div>

        <div className="root-cause-metrics">
          <div>
            <span>Supporting</span>
            <strong>{rootCause.supporting_evidence.length}</strong>
          </div>

          <div>
            <span>Contradicting</span>
            <strong>{rootCause.contradicting_evidence.length}</strong>
          </div>

          <div>
            <span>Source Diversity</span>
            <strong>{rootCause.source_types.length}</strong>
          </div>
        </div>

        <div className="root-cause-sources">
          <span className="root-cause-sources-label">
            Evidence Sources
          </span>

          <div className="root-cause-source-list">
            {rootCause.source_types.map((sourceType) => (
              <span
                key={sourceType}
                className="root-cause-source"
              >
                {sourceType}
              </span>
            ))}
          </div>
        </div>
      </article>
    </section>
  )
}

export default RootCausePanel