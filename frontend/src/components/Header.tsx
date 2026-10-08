type HeaderProps = {
  title: string
  description?: string
}

function Header({
  title,
  description,
}: HeaderProps) {
  return (
    <header className="page-header">
      <div>
        <h1 className="page-title">
          {title}
        </h1>

        {description && (
          <p className="page-description">
            {description}
          </p>
        )}
      </div>

      <div className="header-actions">
        <div
          className="header-notification"
          role="img"
          aria-label="Notifications icon"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
            <path d="M10 21h4" />
          </svg>
        </div>
        <div className="header-profile">
          <div className="header-avatar">
            MG
          </div>

          <span className="header-profile-name">
            Meghan
          </span>
        </div>
      </div>
    </header>
  )
}

export default Header