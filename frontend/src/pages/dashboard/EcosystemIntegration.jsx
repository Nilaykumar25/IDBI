import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Link2, CheckCircle, Send, Building2, Clock } from 'lucide-react'
import apiClient, { transformError } from '../../lib/api'
import ErrorMessage from '../../components/ErrorMessage'
import LoadingSpinner from '../../components/LoadingSpinner'
import { useAuth } from '../../contexts/AuthContext'
import './EcosystemIntegration.css'

const EcosystemIntegration = () => {
  const [scoreData, setScoreData] = useState(null)
  const [aaConsent, setAaConsent] = useState({ status: 'idle', token: null, timestamp: null })
  const [uliPublish, setUliPublish] = useState({ status: 'idle', txId: null, timestamp: null })
  const [lenderMatches, setLenderMatches] = useState([])
  const [loading, setLoading] = useState({ aa: false, uli: false })
  const [error, setError] = useState({ aa: null, uli: null, lenders: null })
  const navigate = useNavigate()
  const { session } = useAuth()

  useEffect(() => {
    const stored = sessionStorage.getItem('currentMSME')
    if (!stored) {
      navigate('/dashboard')
      return
    }
    const data = JSON.parse(stored)
    setScoreData(data.scoreData)
    fetchLenderMatches(data.scoreData.riskBand)
  }, [navigate])

  const handleConsentRequest = async () => {
    setLoading(prev => ({ ...prev, aa: true }))
    setError(prev => ({ ...prev, aa: null }))
    
    try {
      const response = await apiClient.post('/ecosystem/consent', {})
      
      if (response.data.success) {
        setAaConsent({
          status: 'approved',
          token: response.data.data.consentToken,
          timestamp: new Date(response.data.data.timestamp)
        })
      } else {
        setError(prev => ({ ...prev, aa: transformError({ response }) }))
      }
    } catch (err) {
      console.error('AA consent request failed:', err)
      setError(prev => ({ ...prev, aa: transformError(err) }))
    } finally {
      setLoading(prev => ({ ...prev, aa: false }))
    }
  }

  const handlePublishToULI = async () => {
    setLoading(prev => ({ ...prev, uli: true }))
    setError(prev => ({ ...prev, uli: null }))
    
    try {
      const response = await apiClient.post('/ecosystem/publish', {})
      
      if (response.data.success) {
        setUliPublish({
          status: 'success',
          txId: response.data.data.transactionId,
          timestamp: new Date(response.data.data.timestamp)
        })
      } else {
        setError(prev => ({ ...prev, uli: transformError({ response }) }))
      }
    } catch (err) {
      console.error('ULI publish failed:', err)
      setError(prev => ({ ...prev, uli: transformError(err) }))
    } finally {
      setLoading(prev => ({ ...prev, uli: false }))
    }
  }

  const fetchLenderMatches = async (riskBand) => {
    setError(prev => ({ ...prev, lenders: null }))
    
    try {
      const response = await apiClient.get(`/ecosystem/lenders?riskBand=${riskBand}`)
      
      if (response.data.success) {
        // Enhance backend data with additional details
        const backendLenders = response.data.data.lenders
        const enhancedLenders = enhanceBackendLenders(backendLenders, riskBand)
        setLenderMatches(enhancedLenders)
      } else {
        // Fall back to local mock data
        setLenderMatches(generateLocalLenderMatches(riskBand))
        setError(prev => ({ 
          ...prev, 
          lenders: { 
            message: 'Using cached lender data',
            severity: 'warning',
            retryable: false
          } 
        }))
      }
    } catch (err) {
      console.error('Failed to fetch lender matches:', err)
      // Fall back to local mock data if API fails
      setLenderMatches(generateLocalLenderMatches(riskBand))
      const transformedError = transformError(err)
      setError(prev => ({ 
        ...prev, 
        lenders: {
          ...transformedError,
          message: 'Using cached lender data. Connection issue detected.',
          severity: 'warning'
        }
      }))
    }
  }

  const enhanceBackendLenders = (lenders, riskBand) => {
    // Enhance backend lender data with tenure and features
    const featuresByRisk = {
      'Low': [
        ['Quick approval', 'Minimal documentation', 'Collateral-free up to ₹25L'],
        ['Revolving credit', 'Online disbursement', 'Flexible repayment'],
        ['Competitive rates', 'Tax benefits', 'Grace period available']
      ],
      'Medium': [
        ['Tailored for MSMEs', 'Credit score improvement support', 'Part-prepayment allowed'],
        ['Government schemes eligible', 'Mentorship programs', 'Industry-specific rates']
      ],
      'High': [
        ['Fast approval (48 hours)', 'Revenue-based repayment', 'No collateral required'],
        ['Business consulting included', 'Restructuring support', 'Milestone-based disbursement']
      ]
    }

    const tenureByRisk = {
      'Low': ['5 years', '3 years', '7 years'],
      'Medium': ['3 years', '5 years'],
      'High': ['2 years', '3 years']
    }

    return lenders.map((lender, index) => ({
      ...lender,
      tenure: tenureByRisk[riskBand][index] || '3 years',
      features: featuresByRisk[riskBand][index] || ['Standard terms apply']
    }))
  }

  const generateLocalLenderMatches = (riskBand) => {
    const lendersByRisk = {
      'Low': [
        {
          name: 'Prime Bank Ltd',
          productType: 'Business Term Loan',
          interestRate: '8.5% - 10%',
          maxAmount: '₹50 Lakhs',
          tenure: '5 years',
          features: ['Quick approval', 'Minimal documentation', 'Collateral-free up to ₹25L']
        },
        {
          name: 'Digital Finance Corp',
          productType: 'Working Capital Line',
          interestRate: '9% - 11%',
          maxAmount: '₹30 Lakhs',
          tenure: '3 years',
          features: ['Revolving credit', 'Online disbursement', 'Flexible repayment']
        },
        {
          name: 'Growth Capital Partners',
          productType: 'Expansion Loan',
          interestRate: '8% - 9.5%',
          maxAmount: '₹1 Crore',
          tenure: '7 years',
          features: ['Competitive rates', 'Tax benefits', 'Grace period available']
        }
      ],
      'Medium': [
        {
          name: 'MSME Credit Solutions',
          productType: 'Business Loan',
          interestRate: '12% - 14%',
          maxAmount: '₹25 Lakhs',
          tenure: '3 years',
          features: ['Tailored for MSMEs', 'Credit score improvement support', 'Part-prepayment allowed']
        },
        {
          name: 'Regional Development Bank',
          productType: 'SME Term Loan',
          interestRate: '11.5% - 13%',
          maxAmount: '₹40 Lakhs',
          tenure: '5 years',
          features: ['Government schemes eligible', 'Mentorship programs', 'Industry-specific rates']
        }
      ],
      'High': [
        {
          name: 'Alternative Finance Network',
          productType: 'High-Risk Business Loan',
          interestRate: '16% - 20%',
          maxAmount: '₹15 Lakhs',
          tenure: '2 years',
          features: ['Fast approval (48 hours)', 'Revenue-based repayment', 'No collateral required']
        },
        {
          name: 'Turnaround Capital Fund',
          productType: 'Recovery & Growth Loan',
          interestRate: '18% - 22%',
          maxAmount: '₹20 Lakhs',
          tenure: '3 years',
          features: ['Business consulting included', 'Restructuring support', 'Milestone-based disbursement']
        }
      ]
    }

    return lendersByRisk[riskBand] || []
  }

  if (!scoreData) {
    return (
      <div className="ecosystem-container">
        <LoadingSpinner size="large" message="Loading ecosystem integration..." />
      </div>
    )
  }

  return (
    <div className="ecosystem-container">
      <div className="ecosystem-header">
        <h2>Ecosystem Integration</h2>
        <p>Simulated interactions with Account Aggregator, ULI, and OCEN platforms</p>
      </div>

      <div className="integration-grid">
        {/* Account Aggregator Section */}
        <div className="integration-card card">
          <div className="integration-header">
            <Link2 size={24} className="integration-icon" />
            <div>
              <h3>Account Aggregator</h3>
              <p>Consent-based financial data sharing</p>
            </div>
          </div>

          <div className="integration-content">
            {aaConsent.status === 'idle' ? (
              <>
                <p className="integration-description">
                  Request consent to access bank account data via the Account Aggregator framework.
                  This simulates the AA consent flow for secure data sharing.
                </p>
                {error.aa && (
                  <ErrorMessage
                    message={error.aa.message}
                    severity={error.aa.severity}
                    onRetry={error.aa.retryable ? handleConsentRequest : null}
                  />
                )}
                <button 
                  onClick={handleConsentRequest} 
                  disabled={loading.aa}
                  className="btn-integration"
                >
                  {loading.aa ? 'Processing...' : 'Request AA Consent'}
                </button>
              </>
            ) : (
              <div className="integration-result success">
                <CheckCircle size={20} />
                <div className="result-content">
                  <strong>Consent Approved</strong>
                  <p>Token: {aaConsent.token}</p>
                  <p className="timestamp">
                    <Clock size={14} />
                    {aaConsent.timestamp.toLocaleString()}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ULI Section */}
        <div className="integration-card card">
          <div className="integration-header">
            <Send size={24} className="integration-icon" />
            <div>
              <h3>Unified Lending Interface (ULI)</h3>
              <p>Standardized credit protocol</p>
            </div>
          </div>

          <div className="integration-content">
            {uliPublish.status === 'idle' ? (
              <>
                <p className="integration-description">
                  Publish financial health score to ULI for standardized lending interactions.
                  Score: <strong>{scoreData.compositeScore.toFixed(1)}</strong> | 
                  Risk: <strong>{scoreData.riskBand}</strong>
                </p>
                {error.uli && (
                  <ErrorMessage
                    message={error.uli.message}
                    severity={error.uli.severity}
                    onRetry={error.uli.retryable ? handlePublishToULI : null}
                  />
                )}
                <button 
                  onClick={handlePublishToULI} 
                  disabled={loading.uli}
                  className="btn-integration"
                >
                  {loading.uli ? 'Publishing...' : 'Publish to ULI'}
                </button>
              </>
            ) : (
              <div className="integration-result success">
                <CheckCircle size={20} />
                <div className="result-content">
                  <strong>Published Successfully</strong>
                  <p>Transaction ID: {uliPublish.txId}</p>
                  <p className="timestamp">
                    <Clock size={14} />
                    {uliPublish.timestamp.toLocaleString()}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* OCEN Lender Matching Section */}
      <div className="lender-matching-section">
        <div className="section-header">
          <Building2 size={24} />
          <div>
            <h3>OCEN Lender Matching</h3>
            <p>Matched lenders based on {scoreData.riskBand} risk profile</p>
          </div>
        </div>

        {error.lenders && (
          <ErrorMessage
            message={error.lenders.message}
            severity={error.lenders.severity}
          />
        )}

        <div className="lenders-grid">
          {lenderMatches.map((lender, index) => (
            <div key={index} className="lender-card card">
              <div className="lender-header">
                <h4>{lender.name}</h4>
                <span className="product-type">{lender.productType}</span>
              </div>

              <div className="lender-details">
                <div className="detail-row">
                  <span className="detail-label">Interest Rate</span>
                  <span className="detail-value">{lender.interestRate}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Max Amount</span>
                  <span className="detail-value">{lender.maxAmount}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">Tenure</span>
                  <span className="detail-value">{lender.tenure}</span>
                </div>
              </div>

              <div className="lender-features">
                <strong>Key Features:</strong>
                <ul>
                  {lender.features.map((feature, idx) => (
                    <li key={idx}>{feature}</li>
                  ))}
                </ul>
              </div>

              <button className="btn-contact">Contact Lender</button>
            </div>
          ))}
        </div>
      </div>

      <div className="ecosystem-info card">
        <h3>About Ecosystem Integration</h3>
        <p>
          This panel demonstrates how the MSME Financial Health Score system integrates with
          India's digital lending ecosystem:
        </p>
        <ul>
          <li>
            <strong>Account Aggregator (AA):</strong> Secure, consent-based framework for
            financial data sharing between institutions
          </li>
          <li>
            <strong>Unified Lending Interface (ULI):</strong> Standardized protocol for
            seamless credit interactions across lenders
          </li>
          <li>
            <strong>OCEN (Open Credit Enablement Network):</strong> Platform connecting
            borrowers with appropriate lenders based on risk profiles
          </li>
        </ul>
        <p className="info-note">
          Note: This is a simulated demonstration. Production integration would require
          official API credentials and sandbox access from respective platforms.
        </p>
      </div>
    </div>
  )
}

export default EcosystemIntegration
