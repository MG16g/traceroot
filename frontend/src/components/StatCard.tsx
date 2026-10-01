type StatCardTone = 'default' | 'critical' | 'warning' | 'success'

type StatCardProps = {
  label: string
  value: number
  detail: string
  tone?: StatCardTone
}

const icons: Record<StatCardTone, string> = {
  warning: '▶',
  critical: '!',
  default: '▤',
  success: '✓',
}

function StatCard({
  label,
  value,
  detail,
  tone = 'default',
}: StatCardProps) {
  return (
    <article className={`stat-card stat-card-${tone}`}>
      <div className="stat-card-icon" aria-hidden="true">
        {icons[tone]}
      </div>

      <div className="stat-card-content">
        <span className="stat-card-label">
          {label}
        </span>

        <strong className="stat-card-value">
          {value}
        </strong>

        <span className="stat-card-detail">
          {detail}
        </span>
      </div>

      <div
        className="stat-card-wave"
        aria-hidden="true"
      />
    </article>
  )
}

export default StatCard