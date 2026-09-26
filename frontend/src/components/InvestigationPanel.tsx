import type { InvestigationResponse } from '../types/investigation'
import EvidenceList from './EvidenceList'
import HypothesisList from './HypothesisList'
import RootCausePanel from './RootCausePanel'
import RCAReport from './RCAReport'

type InvestigationPanelProps = {
  investigation: InvestigationResponse
}

function InvestigationPanel({
  investigation,
}: InvestigationPanelProps) {
  const rootCauseSupported =
    investigation.root_cause?.status.toLowerCase() === 'supported'

  return (
    <section className="investigation-panel">
      <div className="investigation-panel-header">
        <div>
          <p className="eyebrow">Investigation Result</p>

          <div className="investigation-title-row">
            <h2>{investigation.incident_id}</h2>

            <span
              className={`investigation-status ${
                rootCauseSupported
                  ? 'investigation-status-supported'
                  : ''
              }`}
            >
              {investigation.status}
            </span>
          </div>
        </div>

        <div className="investigation-iteration">
          <span>Iteration</span>
          <strong>{investigation.iteration}</strong>
        </div>
      </div>

      <div className="investigation-summary-grid">
        <div className="investigation-summary-item">
          <span className="summary-label">Current Step</span>
          <strong>{investigation.current_step}</strong>
        </div>

        <div className="investigation-summary-item">
          <span className="summary-label">Actions Executed</span>
          <strong>{investigation.executed_actions.length}</strong>
        </div>

        <div className="investigation-summary-item">
          <span className="summary-label">Evidence Collected</span>
          <strong>{investigation.evidence.length}</strong>
        </div>

        <div className="investigation-summary-item">
          <span className="summary-label">Hypotheses</span>
          <strong>{investigation.hypotheses.length}</strong>
        </div>
      </div>

      <div className="investigation-progress">
        <div className="investigation-progress-header">
          <div>
            <p className="eyebrow">Agent Activity</p>
            <h3>Investigation Progress</h3>
          </div>

          <span className="progress-count">
            {investigation.executed_actions.length} actions
          </span>
        </div>

        {investigation.executed_actions.length > 0 ? (
          <ol className="action-list">
            {investigation.executed_actions.map((action, index) => (
              <li key={`${action}-${index}`} className="action-item">
                <div className="action-marker">
                  <span>{index + 1}</span>
                </div>

                <div className="action-content">
                  <span className="action-name">{action}</span>
                  <span className="action-state">Completed</span>
                </div>
              </li>
            ))}
          </ol>
        ) : (
          <p className="empty-state">
            No investigation actions were recorded.
          </p>
        )}
      </div>
        {/* Evidence */}
        <EvidenceList evidence={investigation.evidence} />

        {/* AI Hypotheses */}
        <HypothesisList hypotheses={investigation.hypotheses} />

        {/* Deterministic Root Cause */}
        <RootCausePanel rootCause={investigation.root_cause} />

        <RCAReport
            report={investigation.final_report}
            incidentId={investigation.incident_id}
        />
    </section>
  )
}

export default InvestigationPanel