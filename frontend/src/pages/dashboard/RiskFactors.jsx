import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from 'recharts'
import { AlertTriangle } from 'lucide-react'
import ErrorMessage from '../../components/ErrorMessage'
import LoadingSpinner from '../../components/LoadingSpinner'
import './RiskFactors.css'

const RiskFactors = () => {
  const [scoreData, setScoreData] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const stored = sessionStorage.getItem('currentMSME')
    if (!stored) {
      navigate('/dashboard')
      return
    }
    const data = JSON.parse(stored)
    setScoreData(data.scoreData)
  }, [navigate])

  if (!scoreData || !scoreData.shapValues) {
    if (!scoreData) {
      return (
        <div className="risk-factors-container">
          <LoadingSpinner size="large" message="Loading risk factors..." />
        </div>
      )
    }
    
    return (
      <div className="risk-factors-container">
        <ErrorMessage
          message="SHAP explainability data is not available for this score computation"
          severity="warning"
          title="Risk Analysis Unavailable"
        />
      </div>
    )
  }

  // Format SHAP values for visualization
  const shapData = Object.entries(scoreData.shapValues)
    .map(([key, value]) => ({
      feature: formatFeatureName(key),
      value: value,
      absValue: Math.abs(value),
      featureValue: scoreData.features?.[key] !== undefined ? (scoreData.features[key] * 100).toFixed(1) : 'N/A'
    }))
    .sort((a, b) => b.absValue - a.absValue)

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="custom-tooltip">
          <p className="tooltip-feature">{data.feature}</p>
          <p className="tooltip-value">SHAP Impact: {data.value.toFixed(3)}</p>
          <p className="tooltip-feature-value">Feature Value: {data.featureValue}</p>
        </div>
      )
    }
    return null
  }

  const getBarColor = (value) => {
    return value >= 0 ? 'var(--risk-low)' : 'var(--risk-high)'
  }

  return (
    <div className="risk-factors-container">
      <div className="risk-factors-header">
        <h2>Risk Factors Analysis</h2>
        <p>SHAP values showing feature contributions to risk classification</p>
      </div>

      <div className="risk-explanation card">
        <AlertTriangle size={20} className="explanation-icon" />
        <div className="explanation-content">
          <h3>Understanding SHAP Values</h3>
          <p>
            SHAP (SHapley Additive exPlanations) values show how each feature influenced the ML risk classification.
            <strong> Positive values</strong> (green) push the score toward <strong>lower risk</strong>, while
            <strong> negative values</strong> (red) push toward <strong>higher risk</strong>.
          </p>
        </div>
      </div>

      <div className="shap-chart-card card">
        <h3>Feature Impact on Risk Classification</h3>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart 
            data={shapData} 
            layout="vertical"
            margin={{ top: 20, right: 30, left: 150, bottom: 20 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="var(--gray-200)" />
            <XAxis type="number" stroke="var(--gray-600)" />
            <YAxis 
              type="category" 
              dataKey="feature" 
              stroke="var(--gray-600)"
              width={140}
              style={{ fontSize: '0.875rem' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine x={0} stroke="var(--gray-400)" strokeWidth={2} />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {shapData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getBarColor(entry.value)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="factors-detail-grid">
        {shapData.map((factor) => (
          <div key={factor.feature} className="factor-detail-card card">
            <div className="factor-header">
              <h4>{factor.feature}</h4>
              <span className={`impact-badge ${factor.value >= 0 ? 'positive' : 'negative'}`}>
                {factor.value >= 0 ? '+ Reduces Risk' : '- Increases Risk'}
              </span>
            </div>
            <div className="factor-metrics">
              <div className="factor-metric">
                <span className="metric-label">Feature Value</span>
                <span className="metric-value">{factor.featureValue}</span>
              </div>
              <div className="factor-metric">
                <span className="metric-label">SHAP Impact</span>
                <span className={`metric-value ${factor.value >= 0 ? 'positive-value' : 'negative-value'}`}>
                  {factor.value.toFixed(3)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="factors-summary card">
        <h3>Key Insights</h3>
        <div className="insights-grid">
          <div className="insight-item">
            <span className="insight-label">Top Risk Reducer</span>
            <span className="insight-value">{shapData[0].feature}</span>
          </div>
          <div className="insight-item">
            <span className="insight-label">Top Risk Increaser</span>
            <span className="insight-value">
              {shapData.find(f => f.value < 0)?.feature || 'None'}
            </span>
          </div>
          <div className="insight-item">
            <span className="insight-label">Total Features Analyzed</span>
            <span className="insight-value">{shapData.length}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper function to format feature names
const formatFeatureName = (name) => {
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim()
}

export default RiskFactors
