import { Routes, Route } from 'react-router-dom'
import Login from '../pages/Login.jsx'
import LocoDashboard from '../pages/LocoDashboard.jsx'
import GatemanDashboard from '../pages/GatemanDashboard.jsx'

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/loco-dashboard" element={<LocoDashboard />} />
      <Route path="/gate-dashboard" element={<GatemanDashboard />} />
    </Routes>
  )
}

export default AppRoutes
