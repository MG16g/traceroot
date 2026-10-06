import { useNavigate } from 'react-router-dom'

import Header from '../components/Header'
import IncidentTable from '../components/IncidentTable'

import type { Incident } from '../types/incident'

const incidents: Incident[] = [
  {
    id: 'INC-001',
    title: 'Checkout payment failures',
    service: 'payment-service',
    severity: 'critical',
    status: 'open',
  },
]

function IncidentsPage() {
  const navigate = useNavigate()

  function handleInvestigate(incidentId: string) {
    navigate(
      `/investigations?incident=${encodeURIComponent(incidentId)}`,
    )
  }

  return (
    <div className="dashboard-page">
      <Header
        title="Incidents"
        description="Monitor production incidents and start root-cause investigations."
      />

      <div className="dashboard-content">
        <section className="incidents-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                Incident Queue
              </p>

              <h2>
                Recent / Active Incidents
              </h2>
            </div>

            <span className="section-meta">
              {incidents.length} active incident
              {incidents.length === 1 ? '' : 's'}
            </span>
          </div>

          <IncidentTable
            incidents={incidents}
            onInvestigate={handleInvestigate}
          />
        </section>
      </div>
    </div>
  )
}

export default IncidentsPage