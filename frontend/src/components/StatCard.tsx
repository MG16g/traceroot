type StatCardTone = 'default' | 'critical' | 'warning' | 'success'

type StatCardProps = {
  label: string
  value: number
  detail: string
  tone?: StatCardTone
}

function StatCard({
  label,
  value,
  detail,
  tone = 'default',
}: StatCardProps) {
  return (
    <article className={`stat-card stat-card-${tone}`}>
      <div className="stat-card-header">
        <span className="stat-card-label">{label}</span>
        <span className="stat-card-indicator" aria-hidden="true" />
      </div>

      <div className="stat-card-value">{value}</div>

      <p className="stat-card-detail">{detail}</p>
    </article>
  )
}

export default StatCard