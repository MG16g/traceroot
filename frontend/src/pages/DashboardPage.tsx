import { Link } from 'react-router-dom'

import Header from '../components/Header'
import StatCard from '../components/StatCard'

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
            Workspace Navigation
        ========================== */}

        <section className="incidents-section">
          <div className="section-heading">
            <div>
              <p className="eyebrow">
                Workspace
              </p>

              <h2>
                TraceRoot Operations
              </h2>
            </div>

            <span className="section-meta">
              Investigation workspace
            </span>
          </div>

          <div className="dashboard-workspace-grid">
            {workspaceLinks.map(
              (workspace) => (
                <Link
                  key={workspace.path}
                  to={workspace.path}
                  className="dashboard-workspace-card"
                >
                  <div className="dashboard-workspace-card-content">
                    <h3>
                      {workspace.title}
                    </h3>

                    <p>
                      {workspace.description}
                    </p>
                  </div>

                  <span
                    className="dashboard-workspace-arrow"
                    aria-hidden="true"
                  >
                    →
                  </span>
                </Link>
              ),
            )}
          </div>
        </section>
      </div>
    </div>
  )
}

export default DashboardPage