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
        <div className="header-notification">
          ♢
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