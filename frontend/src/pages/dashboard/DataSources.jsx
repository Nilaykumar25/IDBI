import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Database, CheckCircle, XCircle, Clock } from 'lucide-react'
import ErrorMessage from '../../components/ErrorMessage'
import LoadingSpinner from '../../components/LoadingSpinner'
import './DataSources.css'

const DataSources = () => {
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

  if (!scoreData) {
    return (
      <div className="data-sources-container">
        <LoadingSpinner size="large" message="Loading data sources..." />
      </div>
    )
  }

  const dataSources = [
    {
      name: 'GST',
      description: 'Goods and Services Tax records',
      icon: <Database size={24} />,
      available: !scoreData.missingDataSources?.includes('GST'),
      data: scoreData.features ? {
        'Revenue Stability': (scoreData.features.revenueStability * 100).toFixed(1),
        'Compliance Score': (scoreData.features.complianceScore * 100).toFixed(1)
      } : {}
    },
    {
      name: 'UPI',
      description: 'Unified Payments Interface transactions',
      icon: <Database size={24} />,
      available: !scoreData.missingDataSources?.includes('UPI'),
      data: scoreData.features ? {
        'Transaction Velocity': (scoreData.features.transactionVelocity * 100).toFixed(1)
      } : {}
    },
    {
      name: 'Account Aggregator',
      description: 'Bank account data via AA framework',
      icon: <Database size={24} />,
      available: !scoreData.missingDataSources?.includes('AA'),
      data: scoreData.features ? {
        'Liquidity Ratio': (scoreData.features.liquidityRatio * 100).toFixed(1)
      } : {}
    },
    {
      name: 'EPFO',
      description: 'Employees Provident Fund Organisation records',
      icon: <Database size={24} />,
      available: !scoreData.missingDataSources?.includes('EPFO'),
      data: scoreData.features ? {
        'Employment Consistency': (scoreData.features.employmentConsistency * 100).toFixed(1)
      } : {}
    }
  ]

  return (
    <div className="data-sources-container">
      <div className="data-sources-header">
        <h2>Data Sources</h2>
        <p>View aggregated data from all connected sources</p>
      </div>

      <div className="data-sources-grid">
        {dataSources.map((source) => (
          <div key={source.name} className={`source-card card ${!source.available ? 'unavailable' : ''}`}>
            <div className="source-header">
              <div className="source-icon">{source.icon}</div>
              <div className="source-title-area">
                <h3>{source.name}</h3>
                <p>{source.description}</p>
              </div>
              <div className="source-status">
                {source.available ? (
                  <CheckCircle size={24} className="status-icon success" />
                ) : (
                  <XCircle size={24} className="status-icon error" />
                )}
              </div>
            </div>

            {source.available ? (
              <div className="source-data">
                <div className="data-freshness">
                  <Clock size={16} />
                  <span>Updated: {new Date(scoreData.computedAt).toLocaleString()}</span>
                </div>
                <div className="data-metrics">
                  {Object.entries(source.data).map(([key, value]) => (
                    <div key={key} className="data-metric">
                      <span className="metric-label">{key}</span>
                      <span className="metric-value">{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="source-error">
                <ErrorMessage
                  message={`Data unavailable from ${source.name}. Score computed with remaining sources.`}
                  type="warning"
                />
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="data-sources-footer">
        <div className="info-card card">
          <h3>About Data Sources</h3>
          <p>
            The financial health score is computed using data from multiple sources to provide
            a comprehensive assessment. Each source contributes specific metrics that reflect
            different aspects of the MSME's financial health.
          </p>
          <ul>
            <li><strong>GST:</strong> Revenue patterns, tax compliance, and filing regularity</li>
            <li><strong>UPI:</strong> Transaction volume, frequency, and payment activity</li>
            <li><strong>Account Aggregator:</strong> Banking behavior, liquidity, and cash flow</li>
            <li><strong>EPFO:</strong> Employment stability, payroll consistency, and workforce size</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default DataSources
