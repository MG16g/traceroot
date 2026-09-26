import type { EvidenceResponse } from '../types/investigation'

type EvidenceListProps = {
  evidence: EvidenceResponse[]
}

function formatScore(score: number) {
  const normalized = score <= 1 ? score * 100 : score

  return `${Math.round(normalized)}%`
}

function EvidenceList({ evidence }: EvidenceListProps) {
  return (
    <section className="reasoning-section">
      <div className="reasoning-section-header">
        <div>
          <p className="eyebrow">Collected Signals</p>
          <h3>Evidence</h3>
        </div>

        <span className="reasoning-count">
          {evidence.length} items
        </span>
      </div>

      {evidence.length > 0 ? (
        <div className="evidence-list">
          {evidence.map((item) => (
            <article key={item.id} className="evidence-card">
              <div className="evidence-card-header">
                <div className="evidence-source">
                  <span
                    className={`source-badge source-${item.source_type.toLowerCase()}`}
                  >
                    {item.source_type}
                  </span>

                  <code>{item.service}</code>
                </div>

                <div className="relevance-score">
                  <span>Relevance</span>
                  <strong>{formatScore(item.relevance_score)}</strong>
                </div>
              </div>

              <p className="evidence-content">
                {item.content}
              </p>

              <div className="evidence-id">
                {item.id}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="empty-state">
          No evidence was collected during this investigation.
        </p>
      )}
    </section>
  )
}

export default EvidenceList