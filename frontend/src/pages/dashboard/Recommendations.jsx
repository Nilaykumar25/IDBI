import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Lightbulb, TrendingUp, DollarSign, Shield, Users } from 'lucide-react'
import LoadingSpinner from '../../components/LoadingSpinner'
import './Recommendations.css'

const Recommendations = () => {
  const [scoreData, setScoreData] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    const stored = sessionStorage.getItem('currentMSME')
    if (!stored) {
      navigate('/dashboard')
      return
    }
    const data = JSON.parse(stored)
    setScoreData(data.scoreData)
    generateRecommendations(data.scoreData)
  }, [navigate])

  const generateRecommendations = (data) => {
    if (!data || !data.shapValues || !data.features) return

    const recs = []
    const shapEntries = Object.entries(data.shapValues)
      .map(([key, value]) => ({ feature: key, shap: value, featureValue: data.features[key] }))
      .sort((a, b) => a.shap - b.shap) // Most negative first (biggest risk contributors)

    // Priority 1: Focus on negative SHAP values (actual risk contributors)
    shapEntries.forEach((entry) => {
      if (entry.shap < 0 && recs.length < 5) {
        const existing = recs.find(r => r.feature === entry.feature)
        if (!existing) {
          recs.push(createRecommendation(entry.feature, entry.featureValue, 'high'))
        }
      }
    })

    // Priority 2: Add recommendations for low feature values
    Object.entries(data.features).forEach(([feature, value]) => {
      if (value < 0.6 && recs.length < 5) {
        const existing = recs.find(r => r.feature === feature)
        if (!existing) {
          recs.push(createRecommendation(feature, value, 'medium'))
        }
      }
    })

    // Priority 3: If we still don't have 3 recommendations, add improvement areas
    if (recs.length < 3) {
      Object.entries(data.features).forEach(([feature, value]) => {
        if (value < 0.8 && recs.length < 5) {
          const existing = recs.find(r => r.feature === feature)
          if (!existing) {
            recs.push(createRecommendation(feature, value, 'medium'))
          }
        }
      })
    }

    // Priority 4: Add positive reinforcement only if we have room and good features
    if (recs.length < 5 && data.riskBand === 'Low') {
      shapEntries.reverse().slice(0, 2).forEach((entry) => {
        if (entry.shap > 0 && entry.featureValue > 0.7 && recs.length < 5) {
          const existing = recs.find(r => r.feature === entry.feature)
          if (!existing) {
            recs.push({
              category: getCategoryForFeature(entry.feature),
              title: `Maintain Strong ${formatFeatureName(entry.feature)}`,
              description: `Your ${formatFeatureName(entry.feature)} is excellent. Continue current practices to sustain this strength.`,
              priority: 'low',
              icon: getIconForCategory(getCategoryForFeature(entry.feature)),
              feature: entry.feature
            })
          }
        }
      })
    }

    setRecommendations(recs.slice(0, 5))
  }

  const createRecommendation = (feature, value, priority) => {
    const category = getCategoryForFeature(feature)
    const formattedFeature = formatFeatureName(feature)
    
    const recommendations = {
      revenueStability: {
        title: 'Improve Revenue Consistency',
        description: 'Focus on diversifying revenue streams and maintaining regular cash flows. Consider contracts with predictable payment terms and expand customer base to reduce volatility.',
        icon: <DollarSign size={24} />
      },
      transactionVelocity: {
        title: 'Increase Transaction Activity',
        description: 'Boost transaction volume and frequency through improved marketing, customer engagement, and operational efficiency. Digital payment adoption can help track and increase transactions.',
        icon: <TrendingUp size={24} />
      },
      liquidityRatio: {
        title: 'Strengthen Liquidity Position',
        description: 'Build cash reserves to cover at least 2-3 months of operating expenses. Optimize working capital by managing receivables and payables more efficiently.',
        icon: <DollarSign size={24} />
      },
      employmentConsistency: {
        title: 'Stabilize Employment and Payroll',
        description: 'Maintain consistent EPFO contributions and reduce employee turnover. Invest in retention programs and ensure regular payroll processing to demonstrate workforce stability.',
        icon: <Users size={24} />
      },
      complianceScore: {
        title: 'Enhance Regulatory Compliance',
        description: 'Ensure timely GST filing and maintain full compliance with all regulatory requirements. Set up automated reminders and consider engaging a tax consultant.',
        icon: <Shield size={24} />
      },
      growthIndicator: {
        title: 'Accelerate Business Growth',
        description: 'Focus on sustainable growth across revenue, transactions, and workforce. Invest in business development and operational scaling while maintaining financial discipline.',
        icon: <TrendingUp size={24} />
      }
    }

    const rec = recommendations[feature] || {
      title: `Improve ${formattedFeature}`,
      description: `Focus on improving your ${formattedFeature.toLowerCase()} through targeted initiatives and monitoring progress regularly.`,
      icon: <Lightbulb size={24} />
    }

    return {
      category,
      title: rec.title,
      description: rec.description,
      priority,
      icon: rec.icon,
      feature
    }
  }

  const getCategoryForFeature = (feature) => {
    const map = {
      revenueStability: 'revenue',
      transactionVelocity: 'revenue',
      liquidityRatio: 'liquidity',
      employmentConsistency: 'employment',
      complianceScore: 'compliance',
      growthIndicator: 'revenue'
    }
    return map[feature] || 'revenue'
  }

  const getIconForCategory = (category) => {
    const icons = {
      revenue: <DollarSign size={24} />,
      liquidity: <DollarSign size={24} />,
      compliance: <Shield size={24} />,
      employment: <Users size={24} />
    }
    return icons[category] || <Lightbulb size={24} />
  }

  const getPriorityClass = (priority) => {
    return `priority-${priority}`
  }

  const getPriorityLabel = (priority) => {
    const labels = {
      high: 'High Priority',
      medium: 'Medium Priority',
      low: 'Good Practice'
    }
    return labels[priority] || priority
  }

  if (!scoreData) {
    return (
      <div className="recommendations-container">
        <LoadingSpinner size="large" message="Generating recommendations..." />
      </div>
    )
  }

  return (
    <div className="recommendations-container">
      <div className="recommendations-header">
        <h2>Actionable Recommendations</h2>
        <p>Targeted guidance to improve financial health score</p>
      </div>

      <div className="risk-context card">
        <div className="context-header">
          <h3>Current Status</h3>
          <span className={`badge badge-${scoreData.riskBand.toLowerCase()}`}>
            {scoreData.riskBand} Risk
          </span>
        </div>
        <p>
          Based on your score of <strong>{scoreData.compositeScore.toFixed(1)}</strong> and 
          <strong> {scoreData.riskBand}</strong> risk classification, we've identified 
          the following areas for improvement.
        </p>
      </div>

      <div className="recommendations-list">
        {recommendations.map((rec, index) => (
          <div key={index} className={`recommendation-card card ${getPriorityClass(rec.priority)}`}>
            <div className="recommendation-header">
              <div className="rec-icon">{rec.icon}</div>
              <div className="rec-title-area">
                <h3>{rec.title}</h3>
                <span className={`priority-badge ${getPriorityClass(rec.priority)}`}>
                  {getPriorityLabel(rec.priority)}
                </span>
              </div>
            </div>
            <p className="recommendation-description">{rec.description}</p>
            <div className="recommendation-footer">
              <span className="category-tag">{rec.category.toUpperCase()}</span>
            </div>
          </div>
        ))}
      </div>

      {recommendations.length === 0 && (
        <div className="empty-recommendations card">
          <Lightbulb size={48} className="empty-icon" />
          <h3>All Looking Good!</h3>
          <p>Your financial health indicators are strong. Continue maintaining current practices.</p>
        </div>
      )}
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

export default Recommendations
