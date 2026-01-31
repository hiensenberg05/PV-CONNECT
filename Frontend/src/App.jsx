import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Home from './pages/home'
import Dashboard from './pages/dashboard'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/home" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/" element={<Navigate to="/home" replace />} />
      </Routes>
    </Router>
  )
}

export default App
