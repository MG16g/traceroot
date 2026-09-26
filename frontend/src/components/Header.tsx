type HeaderProps = {
  title: string
  description?: string
}

function Header({ title, description }: HeaderProps) {
  return (
    <header className="page-header">
      <div>
        <p className="header-context">TraceRoot / Production</p>

        <h1 className="page-title">{title}</h1>

        {description && (
          <p className="page-description">{description}</p>
        )}
      </div>

      <div className="header-actions">
        <div className="environment-badge">
          <span className="environment-indicator" />
          Production
        </div>

        <div className="operational-badge">
          <span className="status-dot" />
          Operational
        </div>
      </div>
    </header>
  )
}

export default Header