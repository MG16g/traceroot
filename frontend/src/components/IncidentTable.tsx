import type { Incident } from '../types/incident'

type IncidentTableProps = {
  incidents: Incident[]
  investigatingIncidentId?: string | null
  onViewDetails?: (incidentId: string) => void
  onInvestigate: (incidentId: string) => void
}

function IncidentTable({
  incidents,
  investigatingIncidentId,
  onViewDetails,
  onInvestigate,
}: IncidentTableProps) {
  return (
    <div className="incident-table-container">
      <table className="incident-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Service</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          {incidents.map((incident) => {
            const isInvestigating =
              investigatingIncidentId ===
              incident.id

            return (
              <tr key={incident.id}>
                <td>
                  <span className="incident-id">
                    {incident.id}
                  </span>
                </td>

                <td>
                  <div className="incident-primary">
                    <span className="incident-title">
                      {incident.title}
                    </span>

                    <span className="incident-description">
                      {incident.description}
                    </span>
                  </div>
                </td>

                <td>
                  <span className="service-name">
                    {incident.service}
                  </span>
                </td>

                <td>
                  <span
                    className={`severity-badge severity-${incident.severity}`}
                  >
                    <span className="badge-dot" />
                    {incident.severity}
                  </span>
                </td>

                <td>
                  <span
                    className={`status-badge status-${incident.status}`}
                  >
                    <span className="status-dot-small" />
                    {incident.status}
                  </span>
                </td>

                <td className="incident-action-cell">
                  <div className="incident-row-actions">
                    {onViewDetails && (
                      <button
                        type="button"
                        className="incident-details-button"
                        onClick={() =>
                          onViewDetails(incident.id)
                        }
                      >
                        View Details
                      </button>
                    )}

                    <button
                      type="button"
                      className="investigate-button"
                      disabled={isInvestigating}
                      onClick={() =>
                        onInvestigate(incident.id)
                      }
                    >
                      {isInvestigating
                        ? 'Investigating...'
                        : 'Investigate'}
                    </button>
                  </div>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export default IncidentTable