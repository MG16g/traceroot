import type { HypothesisResponse } from '../types/investigation'

type HypothesisListProps = {
  hypotheses: HypothesisResponse[]
}

function normalizeConfidence(confidence: number) {
  const normalized =
    confidence <= 1 ? confidence * 100 : confidence

  return Math.max(0, Math.min(100, Math.round(normalized)))
}

function HypothesisList({
  hypotheses,
}: HypothesisListProps) {
  return (
    <section className="reasoning-section">
      <div className="reasoning-section-header">
        <div>
          <p className="eyebrow">AI Reasoning</p>
          <h3>Hypotheses</h3>
        </div>

        <span className="reasoning-count">
          {hypotheses.length}{' '}
          {hypotheses.length === 1 ? 'candidate' : 'candidates'}
        </span>
      </div>

      {hypotheses.length > 0 ? (
        <div className="hypothesis-list">
          {hypotheses.map((hypothesis, index) => {
            const confidence = normalizeConfidence(
              hypothesis.confidence,
            )

            return (
              <article
                key={hypothesis.id}
                className="hypothesis-card"
              >
                <div className="hypothesis-header">
                  <div className="hypothesis-heading">
                    <span className="hypothesis-number">
                      H{index + 1}
                    </span>

                    <span
                      className={`hypothesis-status hypothesis-status-${hypothesis.status.toLowerCase()}`}
                    >
                      {hypothesis.status}
                    </span>
                  </div>

                  <div className="confidence-value">
                    <span>Confidence</span>
                    <strong>{confidence}%</strong>
                  </div>
                </div>

                <p className="hypothesis-description">
                  {hypothesis.description}
                </p>

                <div className="confidence-track">
                  <div
                    className="confidence-fill"
                    style={{ width: `${confidence}%` }}
                  />
                </div>

                <div className="hypothesis-evidence-summary">
                  <div>
                    <span>Supporting Evidence</span>
                    <strong>
                      {hypothesis.supporting_evidence.length}
                    </strong>
                  </div>

                  <div>
                    <span>Contradicting Evidence</span>
                    <strong>
                      {hypothesis.contradicting_evidence.length}
                    </strong>
                  </div>
                </div>

                <div className="hypothesis-id">
                  {hypothesis.id}
                </div>
              </article>
            )
          })}
        </div>
      ) : (
        <p className="empty-state">
          No hypotheses were generated during this investigation.
        </p>
      )}
    </section>
  )
}

export default HypothesisList