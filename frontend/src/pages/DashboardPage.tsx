import { useEffect, useRef, useState } from 'react'

import Header from '../components/Header'
import StatCard from '../components/StatCard'
import IncidentTable from '../components/IncidentTable'
import InvestigationPanel from '../components/InvestigationPanel'
import InvestigationError from '../components/InvestigationError'
import InvestigationTimeline from '../components/InvestigationTimeline'

import { streamInvestigation } from '../services/investigationService'

import type { Incident } from '../types/incident'
import type {
  InvestigationResponse,
  InvestigationStreamEvent,
} from '../types/investigation'


const overviewStats = [
  {
    label: 'Active Incidents',
    value: 1,
    detail: 'Currently open',
    tone: 'warning' as const,
  },
  {
    label: 'Critical Incidents',
    value: 1,
    detail: 'Requires attention',
    tone: 'critical' as const,
  },
  {
    label: 'Investigations',
    value: 1,
    detail: 'Investigation records',
    tone: 'default' as const,
  },
  {
    label: 'Supported RCAs',
    value: 1,
    detail: 'Evidence supported',
    tone: 'success' as const,
  },
]


const incidents: Incident[] = [
  {
    id: 'INC-001',
    title: 'Checkout payment failures',
    service: 'payment-service',
    severity: 'critical',
    status: 'open',
  },
]


function DashboardPage() {
  const [
    investigatingIncidentId,
    setInvestigatingIncidentId,
  ] = useState<string | null>(null)

  const [
    investigationResult,
    setInvestigationResult,
  ] = useState<InvestigationResponse | null>(null)

  const [
    investigationError,
    setInvestigationError,
  ] = useState<string | null>(null)

  const [
    failedIncidentId,
    setFailedIncidentId,
  ] = useState<string | null>(null)

  const [
    streamEvents,
    setStreamEvents,
  ] = useState<InvestigationStreamEvent[]>([])

  const eventSourceRef =
    useRef<EventSource | null>(null)

  useEffect(() => {
    return () => {
      eventSourceRef.current?.close()
      eventSourceRef.current = null
    }
  }, [])


  function handleInvestigate(incidentId: string) {
    // Close any previous investigation stream.
    eventSourceRef.current?.close()
    eventSourceRef.current = null

    // Reset the UI for the new investigation.
    setInvestigatingIncidentId(incidentId)
    setInvestigationError(null)
    setFailedIncidentId(null)
    setInvestigationResult(null)
    setStreamEvents([])

    const eventSource = streamInvestigation(
      incidentId,

      (event) => {
        // Live investigation events.
        if (event.event === 'started') {
          setStreamEvents((current) => [
            ...current,
            event,
          ])

          return
        }

        if (event.event === 'progress') {
          if (event.step === 'triage') {
            return
          }

          setStreamEvents((current) => [
            ...current,
            event,
          ])

          return
        }

        // Investigation finished successfully.
        if (
          event.event === 'completed' &&
          event.data
        ) {
          setStreamEvents((current) => [
            ...current,
            event,
          ])

          setInvestigationResult(event.data)
          setInvestigatingIncidentId(null)

          eventSourceRef.current?.close()
          eventSourceRef.current = null

          return
        }

        // Backend emitted an explicit error event.
        if (event.event === 'investigation_error') {
          setInvestigationError(event.message)
          setFailedIncidentId(incidentId)
          setInvestigatingIncidentId(null)

          eventSourceRef.current?.close()
          eventSourceRef.current = null
        }
      },

      // Network / EventSource failure.
      (message) => {
        setInvestigationError(message)
        setFailedIncidentId(incidentId)
        setInvestigatingIncidentId(null)

        eventSourceRef.current?.close()
        eventSourceRef.current = null
      },
    )

    eventSourceRef.current = eventSource
  }


  return (
    <div className="dashboard-page">
      <Header
        title="Production Incident Intelligence"
        description="Monitor active incidents, investigations, and root-cause analysis across production systems."
      />

      <div className="dashboard-content">

        {/* =========================
            System Overview
        ========================== */}
        <section className="overview-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                System Overview
              </p>

              <h2>
                Incident Operations
              </h2>
            </div>

            <span className="section-meta">
              Production environment
            </span>
          </div>

          <div className="stats-grid">
            {overviewStats.map((stat) => (
              <StatCard
                key={stat.label}
                label={stat.label}
                value={stat.value}
                detail={stat.detail}
                tone={stat.tone}
              />
            ))}
          </div>
        </section>


        {/* =========================
            Incident Queue
        ========================== */}
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
              1 active incident
            </span>
          </div>

          <IncidentTable
            incidents={incidents}
            investigatingIncidentId={
              investigatingIncidentId
            }
            onInvestigate={handleInvestigate}
          />


          {/* =========================
              Live Investigation
          ========================== */}
          {streamEvents.length > 0 && (
            <InvestigationTimeline
              incidentId={
                investigatingIncidentId ??
                investigationResult?.incident_id ??
                failedIncidentId ??
                'Unknown'
              }
              events={streamEvents}
            />
          )}
        </section>


        {/* =========================
            Investigation Error
        ========================== */}
        {investigationError &&
          failedIncidentId && (
            <InvestigationError
              message={investigationError}
              incidentId={failedIncidentId}
              onRetry={() =>
                handleInvestigate(
                  failedIncidentId,
                )
              }
            />
          )}


        {/* =========================
            Investigation Result
        ========================== */}
        {investigationResult && (
          <InvestigationPanel
            investigation={
              investigationResult
            }
          />
        )}
      </div>
    </div>
  )
}


export default DashboardPage