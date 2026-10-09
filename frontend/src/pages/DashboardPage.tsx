
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import Header from '../components/Header'
import StatCard from '../components/StatCard'

import { getIncidents } from '../services/incidentService'
import {
  getInvestigationHistory,
  getRCAReport,
} from '../services/investigationService'

import type { Incident } from '../types/incident'

type DashboardStats = {
  activeIncidents: number | null
  criticalIncidents: number | null
  investigations: number | null
  supportedRCAs: number | null
}

const initialStats: DashboardStats = {
  activeIncidents: null,
  criticalIncidents: null,
  investigations: null,
  supportedRCAs: null,
}

const workspaceLinks = [
  {
    title: 'Incidents',
    description:
      'Monitor active production incidents and start new investigations.',
    path: '/incidents',
  },
  {
    title: 'Investigations',
    description:
      'Review investigation history, evidence, hypotheses, and run comparisons.',
    path: '/investigations',
  },
  {
    title: 'RCA Reports',
    description:
      'Review persisted root-cause analysis reports from completed investigations.',
    path: '/rca-reports',
  },
  {
    title: 'Telemetry',
    description:
      'Explore the logs, metrics, deployments, and evidence used by TraceRoot.',
    path: '/telemetry',
  },
]

function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>(initialStats)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    async function loadDashboard() {
      try {
        const incidents: Incident[] = await getIncidents()

        const activeIncidents = incidents.filter(
          (incident) =>
            incident.status === 'open' ||
            incident.status === 'investigating',
        ).length

        const criticalIncidents = incidents.filter(
          (incident) =>
            incident.severity === 'critical' &&
            incident.status !== 'resolved',
        ).length

        if (active) {
          setStats({
            activeIncidents,
            criticalIncidents,
            investigations: null,
            supportedRCAs: null,
          })
        }

        const historyResults = await Promise.allSettled(
          incidents.map((incident) =>
            getInvestigationHistory(incident.id),
          ),
        )

        const historyFailed = historyResults.some(
          (result) => result.status === 'rejected',
        )

        if (historyFailed) {
          if (active) {
            setError(
              'Some investigation histories could not be loaded.',
            )
          }
          return
        }

        const investigationIds = new Set<string>()

        for (const result of historyResults) {
          if (result.status === 'fulfilled') {
            for (const item of result.value) {
              investigationIds.add(item.investigation_id)
            }
          }
        }

        const ids = Array.from(investigationIds)

        if (active) {
          setStats({
            activeIncidents,
            criticalIncidents,
            investigations: ids.length,
            supportedRCAs: null,
          })
        }

        const reportResults = await Promise.allSettled(
          ids.map((id) => getRCAReport(id)),
        )

        const reportsFailed = reportResults.some(
          (result) => result.status === 'rejected',
        )

        if (reportsFailed) {
          if (active) {
            setError(
              'Some RCA reports could not be loaded.',
            )
          }
          return
        }

        const supportedRCAs = reportResults.filter(
          (result) =>
            result.status === 'fulfilled' &&
            result.value.root_cause_status === 'supported',
        ).length

        if (active) {
          setStats({
            activeIncidents,
            criticalIncidents,
            investigations: ids.length,
            supportedRCAs,
          })
          setError(null)
        }
      } catch (err) {
        if (active) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load dashboard statistics.',
          )
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    void loadDashboard()

    return () => {
      active = false
    }
  }, [])

  const overviewStats = [
    {
      label: 'Active Incidents',
      value: stats.activeIncidents ?? '--',
      detail: 'Open or investigating',
      tone: 'warning' as const,
    },
    {
      label: 'Critical Incidents',
      value: stats.criticalIncidents ?? '--',
      detail: 'Unresolved critical incidents',
      tone: 'critical' as const,
    },
    {
      label: 'Investigations',
      value: stats.investigations ?? '--',
      detail: 'Persisted investigation records',
      tone: 'default' as const,
    },
    {
      label: 'Supported RCAs',
      value: stats.supportedRCAs ?? '--',
      detail: 'Evidence-supported root causes',
      tone: 'success' as const,
    },
  ]

  return (
    <div className="dashboard-page">
      <Header
        title="Production Incident Intelligence"
        description="Monitor active incidents, investigations, and root-cause analysis across production systems."
      />

      <div className="dashboard-content">
        <section className="overview-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">System Overview</p>
              <h2>Incident Operations</h2>
            </div>

            <span className="section-meta">
              Production environment
            </span>
          </div>

          {error && (
            <p role="alert" className="dashboard-stats-error">
              {error}
            </p>
          )}

          {loading && (
            <div
              className="dashboard-loading-status"
              role="status"
              aria-live="polite"
            >
              <span
                className="dashboard-loading-spinner"
                aria-hidden="true"
              />

              <span>Loading operational statistics...</span>
            </div>
          )}

          <div className="stats-grid" aria-busy={loading}>
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

        <section className="incidents-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Workspace</p>
              <h2>TraceRoot Operations</h2>
            </div>

            <span className="section-meta">
              Investigation workspace
            </span>
          </div>

          <div className="dashboard-workspace-grid">
            {workspaceLinks.map((workspace) => (
              <Link
                key={workspace.path}
                to={workspace.path}
                className="dashboard-workspace-card"
              >
                <div className="dashboard-workspace-card-content">
                  <h3>{workspace.title}</h3>
                  <p>{workspace.description}</p>
                </div>

                <span
                  className="dashboard-workspace-arrow"
                  aria-hidden="true"
                >
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M5 12h14" />
                    <path d="m13 6 6 6-6 6" />
                  </svg>
                </span>
              </Link>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}

export default DashboardPage
