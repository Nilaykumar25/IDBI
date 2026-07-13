import React, { useEffect, useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sliders, RotateCcw, TrendingUp, TrendingDown } from 'lucide-react'
import apiClient, { transformError } from '../../lib/api'
import ErrorMessage from '../../components/ErrorMessage'
import LoadingSpinner from '../../components/LoadingSpinner'
import ScoreGauge from '../../components/ScoreGauge'
import './WhatIfSimulator.css'

const WhatIfSimulator = () => {
  const [msmeId, setMsmeId] = useState(null)
  const [sector, setSector] = useState('Trader')
  const [originalScore, setOriginalScore] = useState(null)
  const [originalFeatures, setOriginalFeatures] = useState(null)
  const [originalRiskBand, setOriginalRiskBand] = useState(null)
  const [adjustedFeatures, setAdjustedFeatures] = useState(null)
  const [simulatedScore, setSimulatedScore] = useState(null)
  const [simulatedRiskBand, setSimulatedRiskBand] = useState(null)
  const [expandedFeatures, setExpandedFeatures] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()
  const simulateTimeoutRef = useRef(null)

  useEffect(() => {
    const stored = sessionStorage.getItem('currentMSME')
    if (!stored) {
      navigate('/dashboard')
      return
    }
    const data = JSON.parse(stored)
    setMsmeId(data.msmeId)
    setOriginalScore(data.scoreData.compositeScore)
    setOriginalFeatures(data.scoreData.features)
    setOriginalRiskBand(data.scoreData.riskBand)
    setAdjustedFeatures({ ...data.scoreData.features })
    setSimulatedScore(data.scoreData.compositeScore)
    setSimulatedRiskBand(data.scoreData.riskBand)
    
    // Try to get sector from stored data, default to Trader
    setSector(data.sector || 'Trader')
  }, [navigate])

  const handleFeatureChange = (feature, value) => {
    const newFeatures = { ...adjustedFeatures, [feature]: parseFloat(value) }
    setAdjustedFeatures(newFeatures)
    
    // Debounce simulation calls for smooth real-time updates
    if (simulateTimeoutRef.current) {
      clearTimeout(simulateTimeoutRef.current)
    }
    
    simulateTimeoutRef.current = setTimeout(() => {
      simulateScore(newFeatures)
    }, 100) // 100ms debounce for real-time feel
  }

  const simulateScore = async (features) => {
    setLoading(true)
    setError(null)
    try {
      const response = await apiClient.post('/simulate', {
        msmeId,
        features,
        sector
      })

      if (response.data.success) {
        setSimulatedScore(response.data.data.compositeScore)
        setSimulatedRiskBand(response.data.data.riskBand)
      } else {
        setError({
          message: 'Failed to simulate score',
          severity: 'warning',
          retryable: true
        })
      }
    } catch (err) {
      const transformedError = transformError(err)
      setError(transformedError)
      console.error('Simulation failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    if (adjustedFeatures) {
      simulateScore(adjustedFeatures)
    }
  }

  const handleReset = () => {
    // Clear any pending simulations
    if (simulateTimeoutRef.current) {
      clearTimeout(simulateTimeoutRef.current)
    }
    
    setAdjustedFeatures({ ...originalFeatures })
    setSimulatedScore(originalScore)
    setSimulatedRiskBand(originalRiskBand)
  }

  const toggleFeatureExpansion = (featureKey) => {
    setExpandedFeatures(prev => ({
      ...prev,
      [featureKey]: !prev[featureKey]
    }))
  }

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (simulateTimeoutRef.current) {
        clearTimeout(simulateTimeoutRef.current)
      }
    }
  }, [])

  if (!originalFeatures) {
    return (
      <div className="whatif-container">
        <LoadingSpinner size="large" message="Loading simulator..." />
      </div>
    )
  }

  const scoreDelta = simulatedScore - originalScore
  const riskBandChanged = simulatedRiskBand !== originalRiskBand

  const features = [
    { key: 'revenueStability', label: 'Revenue Stability', description: 'Consistency of revenue over time' },
    { key: 'transactionVelocity', label: 'Transaction Velocity', description: 'Volume and frequency of transactions' },
    { key: 'liquidityRatio', label: 'Liquidity Ratio', description: 'Ability to cover short-term obligations' },
    { key: 'employmentConsistency', label: 'Employment Consistency', description: 'Stability of workforce and payroll' },
    { key: 'complianceScore', label: 'Compliance Score', description: 'Tax filing regularity and compliance' },
    { key: 'growthIndicator', label: 'Growth Indicator', description: 'Business growth trajectory' }
  ]

  return (
    <div className="whatif-container">
      <div className="whatif-header">
        <div>
          <h2>What-If Simulator</h2>
          <p>Adjust features to explore improvement scenarios</p>
        </div>
        <button onClick={handleReset} className="btn-reset">
          <RotateCcw size={18} />
          Reset to Original
        </button>
      </div>

      {error && (
        <ErrorMessage
          message={error.message}
          severity={error.severity}
          onRetry={error.retryable ? handleRetry : null}
          title="Simulation Error"
        />
      )}

      <div className="whatif-content">
        <div className="simulator-panel card">
          <div className="panel-header">
            <Sliders size={20} />
            <h3>Feature Adjustments</h3>
          </div>
          <div className="features-list">
            {features.map((feature) => {
              const isAdjusted = originalFeatures && 
                Math.abs(adjustedFeatures[feature.key] - originalFeatures[feature.key]) > 0.001
              const isExpanded = expandedFeatures[feature.key]
              
              return (
                <div 
                  key={feature.key} 
                  className={`feature-card ${isAdjusted ? 'adjusted' : ''} ${isExpanded ? 'expanded' : 'collapsed'}`}
                >
                  <div 
                    className="feature-card-header"
                    onClick={() => toggleFeatureExpansion(feature.key)}
                  >
                    <div className="feature-card-title">
                      <label>{feature.label}</label>
                      <span className="feature-value">
                        {((adjustedFeatures[feature.key] || 0) * 100).toFixed(0)}
                      </span>
                    </div>
                    <p className="feature-description">{feature.description}</p>
                  </div>
                  
                  {isExpanded && (
                    <div className="feature-slider-container">
                      <input
                        type="range"
                        min="0"
                        max="1"
                        step="0.01"
                        value={adjustedFeatures[feature.key] || 0}
                        onChange={(e) => handleFeatureChange(feature.key, e.target.value)}
                        className="slider"
                      />
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>

        <div className="results-panel">
          <div className="comparison-card card">
            <h3>Score Comparison</h3>
            <div className="comparison-grid">
              <div className="comparison-item">
                <span className="comparison-label">Original Score</span>
                <span className="comparison-value original">{originalScore.toFixed(1)}</span>
                <span className={`badge badge-${originalRiskBand.toLowerCase()}`}>
                  {originalRiskBand} Risk
                </span>
              </div>
              <div className="comparison-arrow">→</div>
              <div className="comparison-item">
                <span className="comparison-label">Simulated Score</span>
                <span className="comparison-value simulated">{simulatedScore.toFixed(1)}</span>
                <span className={`badge badge-${simulatedRiskBand.toLowerCase()}`}>
                  {simulatedRiskBand} Risk
                </span>
              </div>
            </div>

            <div className="delta-display">
              <div className={`delta-badge ${scoreDelta >= 0 ? 'positive' : 'negative'}`}>
                {scoreDelta >= 0 ? <TrendingUp size={20} /> : <TrendingDown size={20} />}
                <span>
                  {scoreDelta >= 0 ? '+' : ''}{scoreDelta.toFixed(1)} points
                </span>
              </div>
              {riskBandChanged && (
                <div className="risk-change-badge">
                  Risk Band Changed: {originalRiskBand} → {simulatedRiskBand}
                </div>
              )}
            </div>
          </div>

          <div className="gauge-comparison">
            <div className="gauge-item">
              <h4>Original</h4>
              <ScoreGauge score={originalScore} size={200} />
            </div>
            <div className="gauge-item">
              <h4>Simulated</h4>
              <ScoreGauge score={simulatedScore} size={200} />
            </div>
          </div>

          <div className="insights-card card">
            <h3>Insights</h3>
            {scoreDelta > 0 ? (
              <p className="insight-positive">
                Your adjustments would improve the financial health score by {scoreDelta.toFixed(1)} points.
                {riskBandChanged && ` This would also improve the risk classification from ${originalRiskBand} to ${simulatedRiskBand}.`}
              </p>
            ) : scoreDelta < 0 ? (
              <p className="insight-negative">
                Your adjustments would decrease the financial health score by {Math.abs(scoreDelta).toFixed(1)} points.
                {riskBandChanged && ` This would worsen the risk classification from ${originalRiskBand} to ${simulatedRiskBand}.`}
              </p>
            ) : (
              <p className="insight-neutral">
                Your adjustments have not significantly changed the financial health score.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default WhatIfSimulator
