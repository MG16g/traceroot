import { Navigate, Route, Routes } from 'react-router-dom'

import AppLayout from './layouts/AppLayout'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<DashboardPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App