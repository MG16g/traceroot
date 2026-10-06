import { Navigate, Route, Routes } from 'react-router-dom'

import AppLayout from './layouts/AppLayout'
import DashboardPage from './pages/DashboardPage'
import IncidentsPage from './pages/IncidentsPage'
import InvestigationsPage from './pages/InvestigationsPage'
import RCAReportsPage from './pages/RCAReportsPage'
import TelemetryPage from './pages/TelemetryPage'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/incidents" element={<IncidentsPage />} />
        <Route path="/investigations" element={<InvestigationsPage />} />
        <Route path="/rca-reports" element={<RCAReportsPage />} />
        <Route path="/telemetry" element={<TelemetryPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App