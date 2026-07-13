import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'
import { TrendingUp, Calendar } from 'lucide-react'
import apiClient, { transformError } from '../../lib/api'
import ErrorMessage from '../../components/ErrorMessage'
import LoadingSpinner from '../../components/LoadingSpinner'
import './TrendAnalysis.css'

const TrendAnalysis = () => {
  const [msmeId, setMsmeId] = useState(null)
  const [historyData, setHistoryData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [dateRange, setDateRange] = useState({ months: 6 })
  const navigate = useNavigate()

  useEffect(() => {
    const stored = sessionStorage.getItem('currentMSME')
    if (!stored) {
      navigate('/dashboard')
      return
    }
    const data = JSON.parse(stored)
    setMsmeId(data.msmeId)
    fetchHistory(data.msmeId)
  }, [navigate])

  const fetchHistory = async (id) => {
    setLoading(true)
    setError(null)
    try {
      // Calculate date range
      const endDate = new Date()
      const startDate = new Date()
      startDate.setMonth(startDate.getMonth() - dateRange.months)

      const response = await apiClient.get(
        `/scores/${id}/history?startDate=${startDate.toISOString().split('T')[0]}&endDate=${endDate.toISOString().split('T')[0]}`
      )

      if (response.data.success) {
        const formattedData = response.data.data.map(record => ({
          date: new Date(record.computedAt).toLocaleDateString(),
          score: record.compositeScore,
          riskBand: record.riskBand,
          timestamp: new Date(record.computedAt)
        }))
        setHistoryData(formattedData)
      } else {
        setError({
          message: response.data.error || 'Failed to fetch history',
          severity: 'error',
          retryable: true
        })
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setHistoryData([])
        setError({
          message: 'No historical data available for this MSME',
          severity: 'info',
          retryable: false
        })
      } else {
        setError(transformError(err))
      }
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    if (msmeId) {
      fetchHistory(msmeId)
    }
  }

  const getRiskColor = (riskBand) => {
    const colors = {
      'Low': 'var(--risk-low)',
      'Medium': 'var(--risk-medium)',
      'High': 'var(--risk-high)'
    }
    return colors[riskBand] || 'var(--gray-500)'
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="custom-tooltip">
          <p className="tooltip-date">{data.date}</p>
          <p className="tooltip-score">Score: {data.score.toFixed(1)}</p>
          <p className={`tooltip-risk badge badge-${data.riskBand.toLowerCase()}`}>
            {data.riskBand} Risk
          </p>
        </div>
      )
    }
    return null
  }

  if (loading) {
    return (
      <div className="trend-analysis-container">
        <LoadingSpinner size="large" message="Loading historical trend data..." />
      </div>
    )
  }

  return (
    <div className="trend-analysis-container">
      <div className="trend-header">
        <div>
          <h2>Trend Analysis</h2>
          <p>Historical financial health score progression</p>
        </div>
        <div className="date-range-selector">
          <Calendar size={18} />
          <select 
            value={dateRange.months}
            onChange={(e) => {
              setDateRange({ months: parseInt(e.target.value) })
              if (msmeId) fetchHistory(msmeId)
            }}
          >
            <option value={3}>Last 3 months</option>
            <option value={6}>Last 6 months</option>
            <option value={12}>Last 12 months</option>
          </select>
        </div>
      </div>

      {error && (
        <ErrorMessage
          message={error.message}
          severity={error.severity}
          onRetry={error.retryable ? handleRetry : null}
          title={error.severity === 'info' ? 'No Data Available' : 'Failed to Load Trend Data'}
        />
      )}

      {historyData.length > 0 ? (
        <>
          <div className="chart-card card">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={historyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--gray-200)" />
                <XAxis 
                  dataKey="date" 
                  stroke="var(--gray-600)"
                  style={{ fontSize: '0.875rem' }}
                />
                <YAxis 
                  domain={[0, 100]}
                  stroke="var(--gray-600)"
                  style={{ fontSize: '0.875rem' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <ReferenceLine y={70} stroke="var(--risk-low)" strokeDasharray="3 3" />
                <ReferenceLine y={40} stroke="var(--risk-medium)" strokeDasharray="3 3" />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke="var(--primary-teal)" 
                  strokeWidth={3}
                  dot={{ r: 5, fill: 'var(--primary-teal)' }}
                  activeDot={{ r: 7 }}
                  name="Financial Health Score"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="trend-summary-grid">
            <div className="summary-card card">
              <h3>Score Range</h3>
              <div className="summary-content">
                <div className="summary-metric">
                  <span className="summary-label">Highest</span>
                  <span className="summary-value">
                    {Math.max(...historyData.map(d => d.score)).toFixed(1)}
                  </span>
                </div>
                <div className="summary-metric">
                  <span className="summary-label">Lowest</span>
                  <span className="summary-value">
                    {Math.min(...historyData.map(d => d.score)).toFixed(1)}
                  </span>
                </div>
                <div className="summary-metric">
                  <span className="summary-label">Average</span>
                  <span className="summary-value">
                    {(historyData.reduce((sum, d) => sum + d.score, 0) / historyData.length).toFixed(1)}
                  </span>
                </div>
              </div>
            </div>

            <div className="summary-card card">
              <h3>Risk Band Distribution</h3>
              <div className="summary-content">
                {['Low', 'Medium', 'High'].map(band => {
                  const count = historyData.filter(d => d.riskBand === band).length
                  const percentage = (count / historyData.length * 100).toFixed(0)
                  return (
                    <div key={band} className="risk-distribution-item">
                      <span className={`badge badge-${band.toLowerCase()}`}>{band}</span>
                      <div className="distribution-bar">
                        <div 
                          className={`distribution-fill risk-${band.toLowerCase()}`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="distribution-value">{percentage}%</span>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </>
      ) : (
        !error && (
          <div className="empty-state card">
            <TrendingUp size={48} className="empty-icon" />
            <h3>No Historical Data</h3>
            <p>There is no historical score data available for this MSME yet.</p>
            <p>Scores will appear here after multiple assessments over time.</p>
          </div>
        )
      )}
    </div>
  )
}

export default TrendAnalysis
