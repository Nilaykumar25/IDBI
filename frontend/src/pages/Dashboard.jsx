import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'
import { BarChart3, Moon, Sun, LogOut } from 'lucide-react'
import MSMESearch from './dashboard/MSMESearch'
import ScoreCard from './dashboard/ScoreCard'
import ScoreCardLayout from './dashboard/ScoreCardLayout'
import RiskFactors from './dashboard/RiskFactors'
import DataSources from './dashboard/DataSources'
import Recommendations from './dashboard/Recommendations'
import WhatIfSimulator from './dashboard/WhatIfSimulator'
import EcosystemIntegration from './dashboard/EcosystemIntegration'
import './Dashboard.css'

const Dashboard = () => {
  const { user, signOut } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await signOut()
      navigate('/login')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <div className="header-brand">
          <div className="brand-logo">
            <BarChart3 size={24} strokeWidth={2.5} />
          </div>
          <div className="brand-info">
            <span className="brand-name">CreditLine</span>
            <span className="brand-tagline">MSME FINANCIAL HEALTH SCORE</span>
          </div>
        </div>
        
        <div className="header-actions">
          <span className="user-email">{user?.email}</span>
          <button 
            onClick={toggleTheme} 
            className="theme-toggle"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
          <button 
            onClick={handleLogout} 
            className="logout-btn"
            aria-label="Logout"
          >
            <LogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </header>

      <main className="dashboard-main">
        <Routes>
          <Route index element={<MSMESearch />} />
          <Route element={<ScoreCardLayout />}>
            <Route path="score-card" element={<ScoreCard />} />
            <Route path="data-sources" element={<DataSources />} />
            <Route path="risk-factors" element={<RiskFactors />} />
            <Route path="recommendations" element={<Recommendations />} />
            <Route path="what-if" element={<WhatIfSimulator />} />
            <Route path="ecosystem" element={<EcosystemIntegration />} />
          </Route>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default Dashboard
