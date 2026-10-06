import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import Header from '../components/Header'
import IncidentTable from '../components/IncidentTable'

import { getIncidents } from '../services/incidentService'

import type { Incident } from '../types/incident'


function IncidentsPage() {
  const navigate = useNavigate()

  const [incidents, setIncidents] = useState<Incident[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let isMounted = true

    async function loadIncidents() {
      try {
        setIsLoading(true)
        setError(null)

        const incidentData = await getIncidents()

        if (!isMounted) {
          return
        }

        setIncidents(incidentData)
      } catch (loadError) {
        if (!isMounted) {
          return
        }

        setError(
          loadError instanceof Error
            ? loadError.message
            : 'Unable to load incidents.',
        )
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadIncidents()

    return () => {
      isMounted = false
    }
  }, [])

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

            {!isLoading && !error && (
              <span className="section-meta">
                {incidents.length} incident
                {incidents.length === 1 ? '' : 's'}
              </span>
            )}
          </div>

          {isLoading && (
            <p className="section-meta">
              Loading incidents...
            </p>
          )}

          {!isLoading && error && (
            <div role="alert">
              <p className="section-meta">
                Unable to load incident queue.
              </p>

              <p>{error}</p>
            </div>
          )}

          {!isLoading &&
            !error &&
            incidents.length === 0 && (
              <p className="section-meta">
                No incidents are currently available.
              </p>
            )}

          {!isLoading &&
            !error &&
            incidents.length > 0 && (
              <IncidentTable
                incidents={incidents}
                onInvestigate={handleInvestigate}
              />
            )}
        </section>
      </div>
    </div>
  )
}

export default IncidentsPage