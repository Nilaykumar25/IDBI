import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertCircle, TrendingUp, Activity } from 'lucide-react'
import ScoreGauge from '../../components/ScoreGauge'
import RiskStamp from '../../components/RiskStamp'
import ErrorMessage from '../../components/ErrorMessage'
import LoadingSpinner from '../../components/LoadingSpinner'
import './ScoreCard.css'

const ScoreCard = () => {
  const [scoreData, setScoreData] = useState(null)
  const [msmeId, setMsmeId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    const stored = sessionStorage.getItem('currentMSME')
    if (!stored) {
      navigate('/dashboard')
      return
    }

    const data = JSON.parse(stored)
    setMsmeId(data.msmeId)
    setScoreData(data.scoreData)
  }, [navigate])

  if (!scoreData) {
    return (
      <div className="scorecard-container">
        <LoadingSpinner size="large" message="Loading assessment report..." />
      </div>
    )
  }

  const getScoreDescription = (score) => {
    if (score >= 70) return 'Strong creditworthiness with positive indicators across all assessment criteria.'
    if (score >= 40) return 'Moderate creditworthiness with select areas requiring review.'
    return 'Elevated credit risk requiring immediate attention and corrective measures.'
  }

  const getTopRiskFactors = () => {
    if (!scoreData.shapValues) return []
    
    const factors = Object.entries(scoreData.shapValues)
      .map(([name, impact]) => ({
        name: formatFeatureName(name),
        impact,
        // FIXED: Positive SHAP = decreases risk (green), Negative SHAP = increases risk (red)
        direction: impact > 0 ? 'decreases' : 'increases'
      }))
      .sort((a, b) => Math.abs(b.impact) - Math.abs(a.impact))
      .slice(0, 3)
    
    return factors
  }

  const getLendingVerdict = (riskBand) => {
    const verdicts = {
      'Low': 'Recommended for standard-rate lending',
      'Medium': 'Requires additional review and risk mitigation measures',
      'High': 'Not recommended at this time — elevated risk indicators'
    }
    return verdicts[riskBand] || 'Assessment pending'
  }

  const generateRecommendations = (data) => {
    if (!data || !data.shapValues || !data.features) return []

    const recs = []
    const shapEntries = Object.entries(data.shapValues)
      .map(([key, value]) => ({ feature: key, shap: value, featureValue: data.features[key] }))
      .sort((a, b) => a.shap - b.shap)

    if (data.riskBand === 'Medium' || data.riskBand === 'High') {
      shapEntries.slice(0, 3).forEach((entry) => {
        if (entry.shap < 0) {
          const rec = createRecommendation(entry.feature)
          if (rec) recs.push(rec.title)
        }
      })
    }

    Object.entries(data.features).forEach(([feature, value]) => {
      if (value < 0.5 && recs.length < 6) {
        const rec = createRecommendation(feature)
        if (rec && !recs.some(r => r.includes(formatFeatureName(feature)))) {
          recs.push(rec.title)
        }
      }
    })

    return recs.slice(0, 6)
  }

  const createRecommendation = (feature) => {
    const recommendations = {
      revenueStability: { title: 'Improve revenue consistency through diversified streams and predictable payment terms' },
      transactionVelocity: { title: 'Increase transaction activity via improved marketing and digital adoption' },
      liquidityRatio: { title: 'Strengthen liquidity by building cash reserves covering 2-3 months of operations' },
      employmentConsistency: { title: 'Stabilize employment with consistent EPFO contributions and retention programs' },
      complianceScore: { title: 'Enhance regulatory compliance through timely GST filing and automated reminders' },
      growthIndicator: { title: 'Accelerate sustainable growth across revenue, transactions, and workforce' }
    }
    return recommendations[feature]
  }

  const generatePDF = () => {
    const doc = new jsPDF()
    const pageWidth = doc.internal.pageSize.getWidth()
    const pageHeight = doc.internal.pageSize.getHeight()
    let yPos = 20

    // File number in top-right corner (monospace)
    doc.setFont('courier', 'bold')
    doc.setFontSize(9)
    doc.setTextColor(107, 114, 128)
    doc.text(`File No: ${msmeId}`, pageWidth - 20, 15, { align: 'right' })

    // Header
    doc.setFontSize(20)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('CreditLine — Financial Health Report', pageWidth / 2, yPos, { align: 'center' })
    yPos += 8

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(107, 114, 128)
    doc.text(`Generated: ${new Date().toLocaleString('en-IN')}`, pageWidth / 2, yPos, { align: 'center' })
    yPos += 15

    // Business Information
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('Business Information', 20, yPos)
    yPos += 7

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.text(`MSME ID: ${msmeId}`, 20, yPos)
    yPos += 5
    doc.text(`Assessment Date: ${new Date(scoreData.computedAt).toLocaleDateString('en-IN')}`, 20, yPos)
    yPos += 12

    // Financial Health Score with stamp
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.text('Financial Health Score', 20, yPos)
    yPos += 10

    doc.setFontSize(32)
    doc.setTextColor(20, 184, 166)
    doc.text(scoreData.compositeScore.toFixed(1), 20, yPos)
    
    // FIXED: Use riskBand instead of mlRiskBand
    const riskBand = scoreData.riskBand || 'Medium'
    doc.setFontSize(16)
    doc.setTextColor(20, 36, 59)
    doc.text(`${riskBand} Risk`, 55, yPos)
    yPos += 3

    // Risk stamp visual (simulated)
    doc.setDrawColor(20, 36, 59)
    doc.setLineWidth(2)
    doc.circle(160, yPos - 10, 15, 'S')
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    const stampColor = riskBand === 'Low' ? [22, 163, 74] : riskBand === 'High' ? [220, 38, 38] : [245, 158, 11]
    doc.setTextColor(...stampColor)
    doc.text(riskBand.toUpperCase(), 160, yPos - 10, { align: 'center' })
    doc.setFontSize(7)
    doc.text('RISK', 160, yPos - 4, { align: 'center' })
    yPos += 5

    // Verdict line
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('Lending Recommendation:', 20, yPos)
    yPos += 5
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(75, 85, 99)
    const verdict = doc.splitTextToSize(getLendingVerdict(riskBand), pageWidth - 40)
    doc.text(verdict, 20, yPos)
    yPos += verdict.length * 5 + 3

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(75, 85, 99)
    const description = doc.splitTextToSize(getScoreDescription(scoreData.compositeScore), pageWidth - 40)
    doc.text(description, 20, yPos)
    yPos += description.length * 4 + 12

    // ML Risk Confidence - FIXED: Use confidence object with proper field names
    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('Machine Learning Risk Classification', 20, yPos)
    yPos += 7

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    
    // FIXED: Access confidence correctly
    const confidence = scoreData.confidence || { low: 0, medium: 0, high: 0 }
    doc.text(`Low Risk Confidence: ${(confidence.low * 100).toFixed(1)}%`, 20, yPos)
    yPos += 5
    doc.text(`Medium Risk Confidence: ${(confidence.medium * 100).toFixed(1)}%`, 20, yPos)
    yPos += 5
    doc.text(`High Risk Confidence: ${(confidence.high * 100).toFixed(1)}%`, 20, yPos)
    yPos += 12

    // Top Risk Factors - FIXED: Correct SHAP interpretation
    const topFactors = getTopRiskFactors()
    if (topFactors.length > 0) {
      doc.setFontSize(11)
      doc.setFont('helvetica', 'bold')
      doc.setTextColor(20, 36, 59)
      doc.text('Top Risk Factors (SHAP Analysis)', 20, yPos)
      yPos += 7

      doc.setFontSize(9)
      doc.setFont('helvetica', 'normal')
      topFactors.forEach((factor, idx) => {
        const sign = factor.impact > 0 ? '+' : ''
        // FIXED: Positive = green (decreases risk), Negative = red (increases risk)
        const color = factor.impact > 0 ? [22, 163, 74] : [220, 38, 38]
        doc.setTextColor(...color)
        doc.text(`${idx + 1}. ${factor.name}: ${sign}${factor.impact.toFixed(3)} (${factor.direction} risk)`, 20, yPos)
        yPos += 5
      })
      yPos += 10
    }

    // Assessment Dimensions
    if (yPos > 220) {
      doc.addPage()
      yPos = 20
    }

    doc.setFontSize(11)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('Assessment Dimensions', 20, yPos)
    yPos += 7

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    Object.entries(scoreData.features || {}).forEach(([key, value]) => {
      doc.text(`${formatFeatureName(key)}: ${(value * 100).toFixed(0)}/100`, 20, yPos)
      yPos += 5
    })
    yPos += 10

    // Recommendations
    const recommendations = generateRecommendations(scoreData)
    if (recommendations.length > 0) {
      if (yPos > 220) {
        doc.addPage()
        yPos = 20
      }

      doc.setFontSize(11)
      doc.setFont('helvetica', 'bold')
      doc.setTextColor(20, 36, 59)
      doc.text('Recommendations', 20, yPos)
      yPos += 7

      doc.setFontSize(8)
      doc.setFont('helvetica', 'normal')
      recommendations.forEach((rec, idx) => {
        if (yPos > 270) {
          doc.addPage()
          yPos = 20
        }
        const recText = doc.splitTextToSize(`${idx + 1}. ${rec}`, pageWidth - 40)
        doc.text(recText, 20, yPos)
        yPos += recText.length * 4 + 2
      })
    }

    // Footer disclaimer on every page
    const addFooter = (pageNum) => {
      doc.setPage(pageNum)
      doc.setFontSize(7)
      doc.setTextColor(107, 114, 128)
      doc.setFont('helvetica', 'italic')
      const footerY = pageHeight - 15
      doc.text('This assessment is generated from alternate data sources and machine learning models.', pageWidth / 2, footerY, { align: 'center' })
      doc.text('It should be paired with additional due diligence before making lending decisions.', pageWidth / 2, footerY + 3, { align: 'center' })
      doc.setFont('helvetica', 'normal')
      doc.text(`Page ${pageNum}`, pageWidth / 2, footerY + 8, { align: 'center' })
    }

    const totalPages = doc.internal.getNumberOfPages()
    for (let i = 1; i <= totalPages; i++) {
      addFooter(i)
    }

    // Save PDF
    doc.save(`MSME_Report_${msmeId}_${new Date().toISOString().split('T')[0]}.pdf`)
  }

  return (
    <div className="scorecard-main-ledger">
      {/* Primary assessment with stamp */}
      <section className="assessment-primary">
          <div className="assessment-score-panel">
            <div className="score-label-ledger">Financial Health Score</div>
            <div className="score-value-ledger">{scoreData.compositeScore.toFixed(1)}</div>
            <div className="score-explanation">{getScoreDescription(scoreData.compositeScore)}</div>
            <ScoreGauge score={scoreData.compositeScore} size={240} />
          </div>
          
          <div className="assessment-stamp-panel">
            <RiskStamp riskBand={scoreData.riskBand} />
          </div>
        </section>

        {/* ML Classification Details */}
        <section className="assessment-section">
          <h3 className="section-title-ledger">
            <TrendingUp size={18} />
            <span>Machine Learning Risk Classification</span>
          </h3>
          <div className="classification-grid">
            <div className="classification-item">
              <div className="classification-label">Low Risk Confidence</div>
              <div className="classification-bar">
                <div 
                  className="classification-fill risk-low" 
                  style={{ width: `${(scoreData.confidence?.low || 0) * 100}%` }}
                />
              </div>
              <div className="classification-value">{((scoreData.confidence?.low || 0) * 100).toFixed(1)}%</div>
            </div>
            <div className="classification-item">
              <div className="classification-label">Medium Risk Confidence</div>
              <div className="classification-bar">
                <div 
                  className="classification-fill risk-medium" 
                  style={{ width: `${(scoreData.confidence?.medium || 0) * 100}%` }}
                />
              </div>
              <div className="classification-value">{((scoreData.confidence?.medium || 0) * 100).toFixed(1)}%</div>
            </div>
            <div className="classification-item">
              <div className="classification-label">High Risk Confidence</div>
              <div className="classification-bar">
                <div 
                  className="classification-fill risk-high" 
                  style={{ width: `${(scoreData.confidence?.high || 0) * 100}%` }}
                />
              </div>
              <div className="classification-value">{((scoreData.confidence?.high || 0) * 100).toFixed(1)}%</div>
            </div>
          </div>
        </section>

        {/* Feature Breakdown */}
        <section className="assessment-section">
          <h3 className="section-title-ledger">
            <Activity size={18} />
            <span>Assessment Dimensions</span>
          </h3>
          <div className="feature-table">
            {Object.entries(scoreData.features || {}).map(([key, value]) => (
              <div key={key} className="feature-row">
                <div className="feature-name-ledger">{formatFeatureName(key)}</div>
                <div className="feature-bar-container">
                  <div 
                    className="feature-bar-fill-ledger" 
                    style={{ width: `${value * 100}%` }}
                  />
                </div>
                <div className="feature-value-ledger">{(value * 100).toFixed(0)}/100</div>
              </div>
            ))}
          </div>
        </section>

        {/* Warning for missing data sources */}
        {scoreData.missingDataSources && scoreData.missingDataSources.length > 0 && (
          <section className="assessment-section warning-section">
            <ErrorMessage
              message={`Incomplete data: ${scoreData.missingDataSources.join(', ')} unavailable. Assessment computed from partial records.`}
              severity="warning"
              title="Data Limitation Notice"
            />
          </section>
        )}

        {/* Document footer */}
        <footer className="assessment-footer">
          <div className="footer-timestamp">
            <AlertCircle size={14} />
            <span>Assessment computed at {new Date(scoreData.computedAt).toLocaleTimeString('en-IN')}</span>
          </div>
          <div className="footer-note">
            This assessment is based on aggregated data from registered sources and machine learning analysis.
          </div>
        </footer>
      </div>
  )
}

const formatFeatureName = (name) => {
  return name
    .replace(/([A-Z])/g, ' $1')
    .replace(/^./, (str) => str.toUpperCase())
    .trim()
}

export default ScoreCard
