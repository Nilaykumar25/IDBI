import { useEffect, useState } from 'react'
import { useNavigate, Link, useLocation, Outlet } from 'react-router-dom'
import { Download } from 'lucide-react'
import jsPDF from 'jspdf'
import LoadingSpinner from '../../components/LoadingSpinner'
import './ScoreCard.css'

const ScoreCardLayout = () => {
  const [scoreData, setScoreData] = useState(null)
  const [msmeId, setMsmeId] = useState(null)
  const navigate = useNavigate()
  const location = useLocation()

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

  // Helper function to format feature names
  const formatFeatureName = (name) => {
    return name
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, (str) => str.toUpperCase())
      .trim()
  }

  // Helper function to get score description
  const getScoreDescription = (score) => {
    if (score >= 70) return 'Strong creditworthiness with positive indicators across all assessment criteria.'
    if (score >= 40) return 'Moderate creditworthiness with select areas requiring review.'
    return 'Elevated credit risk requiring immediate attention and corrective measures.'
  }

  // Helper function to generate recommendations with full details
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
          if (rec) recs.push(rec)
        }
      })
    }

    Object.entries(data.features).forEach(([feature, value]) => {
      if (value < 0.5 && recs.length < 6) {
        const rec = createRecommendation(feature)
        if (rec && !recs.some(r => r.title.includes(formatFeatureName(feature)))) {
          recs.push(rec)
        }
      }
    })

    return recs.slice(0, 6)
  }

  // Helper function to create individual recommendation
  const createRecommendation = (feature) => {
    const recommendations = {
      revenueStability: { 
        title: 'Improve Revenue Consistency',
        description: 'Focus on diversifying revenue streams and maintaining regular cash flows. Consider contracts with predictable payment terms and expand customer base to reduce volatility.'
      },
      transactionVelocity: { 
        title: 'Increase Transaction Activity',
        description: 'Boost transaction volume and frequency through improved marketing, customer engagement, and operational efficiency. Digital payment adoption can help track and increase transactions.'
      },
      liquidityRatio: { 
        title: 'Strengthen Liquidity Position',
        description: 'Build cash reserves to cover at least 2-3 months of operating expenses. Optimize working capital by managing receivables and payables more efficiently.'
      },
      employmentConsistency: { 
        title: 'Stabilize Employment and Payroll',
        description: 'Maintain consistent EPFO contributions and reduce employee turnover. Invest in retention programs and ensure regular payroll processing to demonstrate workforce stability.'
      },
      complianceScore: { 
        title: 'Enhance Regulatory Compliance',
        description: 'Ensure timely GST filing and maintain full compliance with all regulatory requirements. Set up automated reminders and consider engaging a tax consultant.'
      },
      growthIndicator: { 
        title: 'Accelerate Business Growth',
        description: 'Focus on sustainable growth across revenue, transactions, and workforce. Invest in business development and operational scaling while maintaining financial discipline.'
      }
    }
    return recommendations[feature]
  }

  if (!scoreData) {
    return (
      <div className="scorecard-container">
        <LoadingSpinner size="large" message="Loading assessment report..." />
      </div>
    )
  }

  const generatePDF = () => {
    const doc = new jsPDF()
    const pageWidth = doc.internal.pageSize.getWidth()
    const pageHeight = doc.internal.pageSize.getHeight()
    const margin = 20
    const contentWidth = pageWidth - (margin * 2)
    let yPos = margin

    // Helper function to check if we need a new page
    const checkPageBreak = (neededSpace) => {
      if (yPos + neededSpace > pageHeight - 30) {
        doc.addPage()
        yPos = margin
        return true
      }
      return false
    }

    // Helper function for section headers (with orphan protection)
    const addSectionHeader = (title, contentHeight = 20) => {
      // Check if header + minimum content would be orphaned
      if (yPos + 15 + contentHeight > pageHeight - 30) {
        doc.addPage()
        yPos = margin
      }
      
      doc.setFontSize(12)
      doc.setFont('helvetica', 'bold')
      doc.setTextColor(20, 36, 59)
      doc.text(title, margin, yPos)
      yPos += 3
      doc.setLineWidth(0.5)
      doc.setDrawColor(184, 147, 74)
      doc.line(margin, yPos, pageWidth - margin, yPos)
      yPos += 8
    }

    // =================
    // PAGE 1: HEADER & OVERVIEW
    // =================
    
    // File number in top-right corner
    doc.setFont('courier', 'bold')
    doc.setFontSize(9)
    doc.setTextColor(107, 114, 128)
    doc.text(`File No: ${msmeId}`, pageWidth - margin, 15, { align: 'right' })

    // Main title
    doc.setFontSize(22)
    doc.setFont('times', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('Credit Assessment Report', pageWidth / 2, yPos, { align: 'center' })
    yPos += 10

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(107, 114, 128)
    doc.text(`Generated: ${new Date().toLocaleString('en-IN')}`, pageWidth / 2, yPos, { align: 'center' })
    yPos += 15

    // Business Information
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('Business Information', margin, yPos)
    yPos += 6

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(75, 85, 99)
    doc.text(`MSME ID: ${msmeId}`, margin, yPos)
    yPos += 5
    doc.text(`Assessment Date: ${new Date(scoreData.computedAt).toLocaleDateString('en-IN')}`, margin, yPos)
    yPos += 12

    // Financial Health Score Section
    addSectionHeader('FINANCIAL HEALTH SCORE', 30)

    doc.setFontSize(36)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 184, 166)
    doc.text(scoreData.compositeScore.toFixed(1), margin, yPos)
    
    const riskBand = scoreData.riskBand || 'Medium'
    const riskColor = riskBand === 'Low' ? [22, 163, 74] : riskBand === 'High' ? [220, 38, 38] : [245, 158, 11]
    doc.setFontSize(16)
    doc.setTextColor(...riskColor)
    doc.text(`${riskBand} Risk`, margin + 45, yPos)
    yPos += 5

    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(75, 85, 99)
    const description = getScoreDescription(scoreData.compositeScore)
    const descLines = doc.splitTextToSize(description, contentWidth)
    doc.text(descLines, margin, yPos)
    yPos += descLines.length * 4 + 10

    // ML Risk Classification
    checkPageBreak(35)
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('Machine Learning Risk Classification', margin, yPos)
    yPos += 7

    const confidence = scoreData.confidence || { low: 0, medium: 0, high: 0 }
    doc.setFontSize(9)
    doc.setFont('helvetica', 'normal')
    
    // Draw confidence bars
    const barWidth = 80
    const barHeight = 6
    const labelWidth = 50
    
    doc.text('Low Risk:', margin, yPos)
    doc.setFillColor(22, 163, 74)
    doc.rect(margin + labelWidth, yPos - 4, barWidth * confidence.low, barHeight, 'F')
    doc.setDrawColor(200, 200, 200)
    doc.rect(margin + labelWidth, yPos - 4, barWidth, barHeight, 'S')
    doc.text(`${(confidence.low * 100).toFixed(1)}%`, margin + labelWidth + barWidth + 5, yPos)
    yPos += 8

    doc.text('Medium Risk:', margin, yPos)
    doc.setFillColor(245, 158, 11)
    doc.rect(margin + labelWidth, yPos - 4, barWidth * confidence.medium, barHeight, 'F')
    doc.rect(margin + labelWidth, yPos - 4, barWidth, barHeight, 'S')
    doc.text(`${(confidence.medium * 100).toFixed(1)}%`, margin + labelWidth + barWidth + 5, yPos)
    yPos += 8

    doc.text('High Risk:', margin, yPos)
    doc.setFillColor(220, 38, 38)
    doc.rect(margin + labelWidth, yPos - 4, barWidth * confidence.high, barHeight, 'F')
    doc.rect(margin + labelWidth, yPos - 4, barWidth, barHeight, 'S')
    doc.text(`${(confidence.high * 100).toFixed(1)}%`, margin + labelWidth + barWidth + 5, yPos)
    yPos += 15

    // =================
    // DATA SOURCES (continuous flow)
    // =================
    
    addSectionHeader('DATA SOURCES', 30)

    const dataSources = [
      {
        name: 'GST',
        description: 'Goods and Services Tax records',
        available: !scoreData.missingDataSources?.includes('GST'),
        metrics: scoreData.features ? {
          'Revenue Stability': (scoreData.features.revenueStability * 100).toFixed(1),
          'Compliance Score': (scoreData.features.complianceScore * 100).toFixed(1)
        } : {}
      },
      {
        name: 'UPI',
        description: 'Unified Payments Interface transactions',
        available: !scoreData.missingDataSources?.includes('UPI'),
        metrics: scoreData.features ? {
          'Transaction Velocity': (scoreData.features.transactionVelocity * 100).toFixed(1)
        } : {}
      },
      {
        name: 'Account Aggregator',
        description: 'Bank account data via AA framework',
        available: !scoreData.missingDataSources?.includes('AA'),
        metrics: scoreData.features ? {
          'Liquidity Ratio': (scoreData.features.liquidityRatio * 100).toFixed(1)
        } : {}
      },
      {
        name: 'EPFO',
        description: 'Employees Provident Fund Organisation records',
        available: !scoreData.missingDataSources?.includes('EPFO'),
        metrics: scoreData.features ? {
          'Employment Consistency': (scoreData.features.employmentConsistency * 100).toFixed(1)
        } : {}
      }
    ]

    dataSources.forEach((source, idx) => {
      checkPageBreak(25)
      
      doc.setFontSize(10)
      doc.setFont('helvetica', 'bold')
      doc.setTextColor(20, 36, 59)
      doc.text(`${idx + 1}. ${source.name}`, margin, yPos)
      
      doc.setFontSize(8)
      doc.setFont('helvetica', 'italic')
      doc.setTextColor(107, 114, 128)
      doc.text(source.description, margin + 5, yPos + 4)
      yPos += 9

      if (source.available) {
        doc.setFontSize(9)
        doc.setFont('helvetica', 'normal')
        doc.setTextColor(22, 163, 74)
        doc.text('✓ Connected', margin + 5, yPos)
        doc.setTextColor(75, 85, 99)
        doc.text(`Updated: ${new Date(scoreData.computedAt).toLocaleString('en-IN')}`, margin + 30, yPos)
        yPos += 6

        Object.entries(source.metrics).forEach(([key, value]) => {
          checkPageBreak(6)
          doc.text(`  • ${key}: ${value}`, margin + 5, yPos)
          yPos += 5
        })
      } else {
        doc.setTextColor(220, 38, 38)
        doc.text('✗ Unavailable', margin + 5, yPos)
        yPos += 5
      }
      yPos += 3
    })

    // =================
    // RISK FACTORS (continuous flow)
    // =================
    
    if (scoreData.shapValues) {
      yPos += 5
      addSectionHeader('RISK FACTORS ANALYSIS', 25)

      doc.setFontSize(9)
      doc.setFont('helvetica', 'normal')
      doc.setTextColor(75, 85, 99)
      const shapIntro = 'SHAP values show how each feature influenced the ML risk classification. Positive values (green) reduce risk, negative values (red) increase risk.'
      const introLines = doc.splitTextToSize(shapIntro, contentWidth)
      doc.text(introLines, margin, yPos)
      yPos += introLines.length * 4 + 8

      const shapData = Object.entries(scoreData.shapValues)
        .map(([key, value]) => ({
          feature: formatFeatureName(key),
          rawKey: key,
          value: value,
          featureValue: scoreData.features?.[key] !== undefined ? (scoreData.features[key] * 100).toFixed(1) : 'N/A'
        }))
        .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))

      shapData.forEach((factor, idx) => {
        checkPageBreak(12)
        
        const color = factor.value >= 0 ? [22, 163, 74] : [220, 38, 38]
        const sign = factor.value >= 0 ? '+' : ''
        
        doc.setFontSize(9)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(20, 36, 59)
        doc.text(`${idx + 1}. ${factor.feature}`, margin, yPos)
        yPos += 5

        doc.setFont('helvetica', 'normal')
        doc.setTextColor(75, 85, 99)
        doc.text(`Feature Value: ${factor.featureValue}`, margin + 5, yPos)
        
        doc.setTextColor(...color)
        doc.text(`SHAP Impact: ${sign}${factor.value.toFixed(3)}`, margin + 60, yPos)
        doc.text(factor.value >= 0 ? '(Reduces Risk)' : '(Increases Risk)', margin + 100, yPos)
        yPos += 7
      })
    }

    // =================
    // RECOMMENDATIONS (continuous flow)
    // =================
    
    yPos += 5
    addSectionHeader('RECOMMENDATIONS', 20)

    const recommendations = generateRecommendations(scoreData)
    
    if (recommendations.length > 0) {
      recommendations.forEach((rec, idx) => {
        checkPageBreak(25)
        
        doc.setFontSize(10)
        doc.setFont('helvetica', 'bold')
        doc.setTextColor(20, 36, 59)
        doc.text(`${idx + 1}. ${rec.title}`, margin, yPos)
        yPos += 6

        doc.setFontSize(9)
        doc.setFont('helvetica', 'normal')
        doc.setTextColor(75, 85, 99)
        const descLines = doc.splitTextToSize(rec.description, contentWidth - 10)
        doc.text(descLines, margin + 5, yPos)
        yPos += descLines.length * 4 + 5
      })
    } else {
      doc.setFontSize(9)
      doc.setFont('helvetica', 'italic')
      doc.setTextColor(75, 85, 99)
      doc.text('All financial health indicators are strong. Continue maintaining current practices.', margin, yPos)
      yPos += 10
    }

    // =================
    // ECOSYSTEM (continuous flow)
    // =================
    
    yPos += 5
    addSectionHeader('ECOSYSTEM INTEGRATION', 20)

    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(20, 36, 59)
    doc.text('Available Integrations', margin, yPos)
    yPos += 7

    const ecosystemItems = [
      {
        title: 'Account Aggregator Framework',
        description: 'Securely share financial data with lenders using the AA framework for faster loan processing.'
      },
      {
        title: 'Unified Lending Interface (ULI)',
        description: 'Connect with multiple digital lenders through a single standardized interface.'
      },
      {
        title: 'OCEN Lender Matching',
        description: 'Get matched with suitable lenders based on your credit profile and business needs.'
      }
    ]

    ecosystemItems.forEach((item) => {
      checkPageBreak(15)
      
      doc.setFontSize(9)
      doc.setFont('helvetica', 'bold')
      doc.setTextColor(20, 36, 59)
      doc.text(`• ${item.title}`, margin, yPos)
      yPos += 5

      doc.setFont('helvetica', 'normal')
      doc.setTextColor(75, 85, 99)
      const descLines = doc.splitTextToSize(item.description, contentWidth - 10)
      doc.text(descLines, margin + 5, yPos)
      yPos += descLines.length * 4 + 5
    })

    // =================
    // FOOTER ON ALL PAGES
    // =================
    
    const addFooter = (pageNum) => {
      doc.setPage(pageNum)
      doc.setFontSize(7)
      doc.setTextColor(107, 114, 128)
      doc.setFont('helvetica', 'italic')
      const footerY = pageHeight - 15
      doc.text('This assessment is generated from alternate data sources and machine learning models.', pageWidth / 2, footerY, { align: 'center' })
      doc.text('It should be paired with additional due diligence before making lending decisions.', pageWidth / 2, footerY + 3, { align: 'center' })
      doc.setFont('helvetica', 'normal')
      doc.text(`Page ${pageNum} of ${doc.internal.getNumberOfPages()}`, pageWidth / 2, footerY + 8, { align: 'center' })
    }

    const totalPages = doc.internal.getNumberOfPages()
    for (let i = 1; i <= totalPages; i++) {
      addFooter(i)
    }

    // Save PDF
    doc.save(`MSME_Report_${msmeId}_${new Date().toISOString().split('T')[0]}.pdf`)
  }

  return (
    <div className="scorecard-container">
      <div className="scorecard-header-ledger">
        <div className="header-file-info">
          <div className="file-number">File No: {msmeId}</div>
          <div className="file-title">Credit Assessment Report</div>
          <div className="file-date">Issued: {new Date(scoreData.computedAt).toLocaleDateString('en-IN')}</div>
        </div>
        <button onClick={generatePDF} className="btn-download-report">
          <Download size={18} />
          Download Report
        </button>
        <nav className="scorecard-tabs">
          <Link 
            to="/dashboard/score-card" 
            className={`nav-tab ${location.pathname === '/dashboard/score-card' ? 'active' : ''}`}
          >
            Overview
          </Link>
          <Link 
            to="/dashboard/data-sources" 
            className={`nav-tab ${location.pathname === '/dashboard/data-sources' ? 'active' : ''}`}
          >
            Data Sources
          </Link>
          <Link 
            to="/dashboard/risk-factors" 
            className={`nav-tab ${location.pathname === '/dashboard/risk-factors' ? 'active' : ''}`}
          >
            Risk Factors
          </Link>
          <Link 
            to="/dashboard/recommendations" 
            className={`nav-tab ${location.pathname === '/dashboard/recommendations' ? 'active' : ''}`}
          >
            Recommendations
          </Link>
          <Link 
            to="/dashboard/what-if" 
            className={`nav-tab ${location.pathname === '/dashboard/what-if' ? 'active' : ''}`}
          >
            Scenario Analysis
          </Link>
          <Link 
            to="/dashboard/ecosystem" 
            className={`nav-tab ${location.pathname === '/dashboard/ecosystem' ? 'active' : ''}`}
          >
            Ecosystem
          </Link>
        </nav>
      </div>

      <Outlet />
    </div>
  )
}

export default ScoreCardLayout
