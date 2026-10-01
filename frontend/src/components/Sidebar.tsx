import { NavLink } from 'react-router-dom'

type NavigationItem = {
  label: string
  path: string
  icon: string
}

const navigationItems: NavigationItem[] = [
  
  {
    label: 'Dashboard',
    path: '/',
    icon: '▦',
  },
  {
    label: 'Incidents',
    path: '/incidents',
    icon: '△',
  },
  {
    label: 'Investigations',
    path: '/investigations',
    icon: '⌕',
  },
  {
    label: 'RCA Reports',
    path: '/rca-reports',
    icon: '▤',
  },
  {
    label: 'Telemetry',
    path: '/telemetry',
    icon: '⌁',
  },

]

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">TR</div>

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
            <span className="nav-icon" aria-hidden="true">
              {item.icon}
            </span>

            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="system-status">
          <span className="status-dot" />

          <div>
            <div className="status-title">System Operational</div>
            <div className="status-subtitle">TraceRoot Engine</div>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar