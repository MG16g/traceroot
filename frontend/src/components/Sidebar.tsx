
import { NavLink } from 'react-router-dom'

type NavigationItem = {
  label: string
  path: string
  icon: 'dashboard' | 'incidents' | 'investigations' | 'reports' | 'telemetry'
}

const navigationItems: NavigationItem[] = [
  { label: 'Dashboard', path: '/', icon: 'dashboard' },
  { label: 'Incidents', path: '/incidents', icon: 'incidents' },
  { label: 'Investigations', path: '/investigations', icon: 'investigations' },
  { label: 'RCA Reports', path: '/rca-reports', icon: 'reports' },
  { label: 'Telemetry', path: '/telemetry', icon: 'telemetry' },
]

function NavigationIcon({ name }: { name: NavigationItem['icon'] }) {
  const common = {
    width: 18,
    height: 18,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth: 1.8,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    'aria-hidden': true as const,
  }

  switch (name) {
    case 'dashboard':
      return (
        <svg {...common}>
          <rect x="3" y="3" width="7" height="7" rx="1.5" />
          <rect x="14" y="3" width="7" height="7" rx="1.5" />
          <rect x="3" y="14" width="7" height="7" rx="1.5" />
          <rect x="14" y="14" width="7" height="7" rx="1.5" />
        </svg>
      )
    case 'incidents':
      return (
        <svg {...common}>
          <path d="M12 3 2 20h20L12 3Z" />
          <path d="M12 9v5" />
          <path d="M12 17h.01" />
        </svg>
      )
    case 'investigations':
      return (
        <svg {...common}>
          <circle cx="10.5" cy="10.5" r="6.5" />
          <path d="m16 16 5 5" />
          <path d="M8 10.5h5" />
          <path d="M10.5 8v5" />
        </svg>
      )
    case 'reports':
      return (
        <svg {...common}>
          <path d="M6 3h9l4 4v14H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Z" />
          <path d="M14 3v5h5" />
          <path d="M8 13h8M8 17h6" />
        </svg>
      )
    case 'telemetry':
      return (
        <svg {...common}>
          <path d="M3 12h4l3-7 4 14 3-7h4" />
        </svg>
      )
  }
}

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark" aria-hidden="true">
          TR
        </div>

        <div>
          <div className="brand-name">TraceRoot</div>
          <div className="brand-subtitle">Incident Intelligence</div>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Primary navigation">
        <p className="nav-section-label">Workspace</p>

        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `nav-item${isActive ? ' nav-item-active' : ''}`
            }
          >
            <span className="nav-icon">
              <NavigationIcon name={item.icon} />
            </span>

            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <span className="status-dot" aria-hidden="true" />

          <div>
            <div className="status-title">TraceRoot Engine</div>
            <div className="status-subtitle">
              Incident Investigation Platform
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
