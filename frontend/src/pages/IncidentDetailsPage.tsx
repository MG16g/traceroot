import { useEffect, useState } from 'react'
import {
  Link,
  useNavigate,
  useParams,
} from 'react-router-dom'

import Header from '../components/Header'

import {
  getIncident,
  updateIncidentStatus,
} from '../services/incidentService'

import type { Incident } from '../types/incident'

function IncidentDetailsPage() {
  const navigate = useNavigate()

  const { incidentId } = useParams<{
    incidentId: string
  }>()

  const [incident, setIncident] =
    useState<Incident | null>(null)

  const [isLoading, setIsLoading] =
    useState(true)

  const [error, setError] =
    useState<string | null>(null)

  const [
    isUpdatingStatus,
    setIsUpdatingStatus,
  ] = useState(false)

  const [statusError, setStatusError] =
    useState<string | null>(null)

  const hasIncidentId =
    typeof incidentId === 'string' &&
    incidentId.length > 0

  useEffect(() => {
    if (!incidentId) {
      return
    }

    let isMounted = true

    async function loadIncident() {
      try {
        const incidentData =
          await getIncident(incidentId!)

        if (!isMounted) {
          return
        }

        setIncident(incidentData)
        setError(null)
      } catch (loadError) {
        if (!isMounted) {
          return
        }

        setError(
          loadError instanceof Error
            ? loadError.message
            : 'Unable to load incident.',
        )
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    void loadIncident()

    return () => {
      isMounted = false
    }
  }, [incidentId])

  async function handleStatusUpdate(
    nextStatus: Incident['status'],
  ) {
    if (!incident) {
      return
    }

    try {
      setIsUpdatingStatus(true)
      setStatusError(null)

      const updatedIncident =
        await updateIncidentStatus(
          incident.id,
          nextStatus,
        )

      setIncident(updatedIncident)
    } catch (updateError) {
      setStatusError(
        updateError instanceof Error
          ? updateError.message
          : 'Unable to update incident status.',
      )
    } finally {
      setIsUpdatingStatus(false)
    }
  }

  return (
    <div className="dashboard-page">
      <Header
        title="Incident Details"
        description="Inspect and manage a production incident."
      />

      <div className="dashboard-content">
        <section className="incidents-section">
          <Link
            to="/incidents"
            className="rca-back-link"
          >
            ← Back to Incidents
          </Link>

          <div className="section-heading">
            <div>
              <p className="eyebrow">
                Incident Workspace
              </p>

              <h2>
                {incident?.title ??
                  incidentId ??
                  'Unknown Incident'}
              </h2>
            </div>
          </div>

          {!hasIncidentId && (
            <div role="alert">
              <p className="section-meta">
                Unable to load incident.
              </p>

              <p>Incident ID is missing.</p>
            </div>
          )}

          {hasIncidentId && isLoading && (
            <p className="section-meta">
              Loading incident...
            </p>
          )}

          {!isLoading && error && (
            <div role="alert">
              <p className="section-meta">
                Unable to load incident.
              </p>

              <p>{error}</p>
            </div>
          )}

          {!isLoading &&
            !error &&
            incident && (
              <>
                <div className="incident-details-grid">
                  <div>
                    <span className="section-meta">
                      Incident ID
                    </span>

                    <p>{incident.id}</p>
                  </div>

                  <div>
                    <span className="section-meta">
                      Service
                    </span>

                    <p>{incident.service}</p>
                  </div>

                  <div>
                    <span className="section-meta">
                      Severity
                    </span>

                    <p>
                      <span
                        className={`severity-badge severity-${incident.severity}`}
                      >
                        <span className="badge-dot" />

                        {incident.severity}
                      </span>
                    </p>
                  </div>

                  <div>
                    <span className="section-meta">
                      Status
                    </span>

                    <p>
                      <span
                        className={`status-badge status-${incident.status}`}
                      >
                        <span className="status-dot-small" />

                        {incident.status}
                      </span>
                    </p>
                  </div>

                  <div>
                    <span className="section-meta">
                      Created
                    </span>

                    <p>
                      {new Date(
                        incident.created_at,
                      ).toLocaleString()}
                    </p>
                  </div>

                  <div className="incident-details-description">
                    <span className="section-meta">
                      Description
                    </span>

                    <p>
                      {incident.description}
                    </p>
                  </div>
                </div>

                <div className="incident-details-actions">
                  <div>
                    <p className="eyebrow">
                      Incident Lifecycle
                    </p>

                    <div className="incident-lifecycle-actions">
                      {incident.status ===
                        'open' && (
                        <button
                          type="button"
                          disabled={
                            isUpdatingStatus
                          }
                          onClick={() =>
                            void handleStatusUpdate(
                              'investigating',
                            )
                          }
                        >
                          {isUpdatingStatus
                            ? 'Updating...'
                            : 'Mark Investigating'}
                        </button>
                      )}

                      {incident.status ===
                        'investigating' && (
                        <button
                          type="button"
                          disabled={
                            isUpdatingStatus
                          }
                          onClick={() =>
                            void handleStatusUpdate(
                              'resolved',
                            )
                          }
                        >
                          {isUpdatingStatus
                            ? 'Updating...'
                            : 'Resolve Incident'}
                        </button>
                      )}

                      {incident.status ===
                        'resolved' && (
                        <span className="section-meta">
                          This incident has
                          been resolved.
                        </span>
                      )}
                    </div>

                    {statusError && (
                      <p role="alert">
                        {statusError}
                      </p>
                    )}
                  </div>

                  <div className="incident-operational-actions">
                    <button
                      type="button"
                      onClick={() =>
                        navigate(
                          `/telemetry?incident=${encodeURIComponent(
                            incident.id,
                          )}`,
                        )
                      }
                    >
                      View Telemetry
                    </button>

                    <button
                      type="button"
                      className="investigate-button"
                      onClick={() =>
                        navigate(
                          `/investigations?incident=${encodeURIComponent(
                            incident.id,
                          )}`,
                        )
                      }
                    >
                      Start Investigation
                    </button>
                  </div>
                </div>
              </>
            )}
        </section>
      </div>
    </div>
  )
}

export default IncidentDetailsPage