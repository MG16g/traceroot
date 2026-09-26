import type { Incident } from '../types/incident'

type IncidentTableProps = {
  incidents: Incident[]
  investigatingIncidentId?: string | null
  onInvestigate: (incidentId: string) => void
}

function IncidentTable({
  incidents,
  investigatingIncidentId,
  onInvestigate,
}: IncidentTableProps) {
  return (
    <div className="incident-table-container">
      <table className="incident-table">
        <thead>
          <tr>
            <th>Incident</th>
            <th>Service</th>
            <th>Severity</th>
            <th>Status</th>
            <th>
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>

        <tbody>
          {incidents.map((incident) => {
            const isInvestigating =
              investigatingIncidentId === incident.id

            return (
              <tr key={incident.id}>
                <td>
                  <div className="incident-primary">
                    <span className="incident-id">{incident.id}</span>
                    <span className="incident-title">
                      {incident.title}
                    </span>
                  </div>
                </td>

                <td>
                  <code className="service-name">
                    {incident.service}
                  </code>
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
                    {incident.status}
                  </span>
                </td>

                <td className="incident-action-cell">
                  <button
                    type="button"
                    className="investigate-button"
                    disabled={isInvestigating}
                    onClick={() => onInvestigate(incident.id)}
                  >
                    {isInvestigating
                      ? 'Investigating...'
                      : 'Investigate'}

                    {!isInvestigating && (
                      <span aria-hidden="true">→</span>
                    )}
                  </button>
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