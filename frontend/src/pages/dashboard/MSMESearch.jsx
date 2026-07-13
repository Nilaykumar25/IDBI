import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, Database, CreditCard, Users } from 'lucide-react'
import apiClient, { transformError } from '../../lib/api'
import ErrorMessage from '../../components/ErrorMessage'
import LoadingSpinner from '../../components/LoadingSpinner'
import './MSMESearch.css'

const MSMESearch = () => {
  const [msmeId, setMsmeId] = useState('')
  const [gstNumber, setGstNumber] = useState('')
  const [upiId, setUpiId] = useState('')
  const [aaConsentToken, setAaConsentToken] = useState('')
  const [epfoEstablishmentId, setEpfoEstablishmentId] = useState('')
  const [sector, setSector] = useState('Trader')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeSource, setActiveSource] = useState('basic')
  const navigate = useNavigate()

  const dataSources = [
    { id: 'basic', label: 'Basic Info', code: 'MSME', icon: FileText, fields: ['msmeId', 'sector'] },
    { id: 'gst', label: 'GST Records', code: 'GST', icon: FileText, fields: ['gstNumber'] },
    { id: 'upi', label: 'UPI Transactions', code: 'UPI', icon: CreditCard, fields: ['upiId'] },
    { id: 'aa', label: 'Account Aggregator', code: 'AA', icon: Database, fields: ['aaConsentToken'] },
    { id: 'epfo', label: 'EPFO Registry', code: 'EPFO', icon: Users, fields: ['epfoEstablishmentId'] }
  ]

  const getSourceStatus = (sourceId) => {
    if (sourceId === 'basic') return msmeId && sector ? 'complete' : 'pending'
    if (sourceId === 'gst') return gstNumber ? 'complete' : 'pending'
    if (sourceId === 'upi') return upiId ? 'complete' : 'pending'
    if (sourceId === 'aa') return aaConsentToken ? 'complete' : 'pending'
    if (sourceId === 'epfo') return epfoEstablishmentId ? 'complete' : 'pending'
    return 'pending'
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      const response = await apiClient.post('/scores', {
        msmeId,
        gstNumber,
        upiId,
        aaConsentToken,
        epfoEstablishmentId,
        sector
      })

      if (response.data.success) {
        sessionStorage.setItem('currentMSME', JSON.stringify({
          msmeId,
          scoreData: response.data.data,
          sector
        }))
        
        navigate('/dashboard/score-card')
      } else {
        setError({
          message: response.data.error || 'Failed to compute score',
          severity: 'error',
          retryable: true
        })
      }
    } catch (err) {
      setError(transformError(err))
    } finally {
      setLoading(false)
    }
  }

  const handleRetry = () => {
    setError(null)
    handleSubmit({ preventDefault: () => {} })
  }

  return (
    <div className="msme-search-container">
      {/* Left rail: Data source file tabs */}
      <aside className="data-source-rail">
        <div className="data-source-rail-header">
          <h3>Data Sources</h3>
        </div>
        <ul className="data-source-tabs">
          {dataSources.map(source => {
            const Icon = source.icon
            const status = getSourceStatus(source.id)
            return (
              <li
                key={source.id}
                className={`data-source-tab ${activeSource === source.id ? 'active' : ''}`}
                onClick={() => setActiveSource(source.id)}
              >
                <span className={`source-status-dot ${status}`} />
                <div>
                  <div className="data-source-label">{source.label}</div>
                  <div className="data-source-code">{source.code}</div>
                </div>
              </li>
            )
          })}
        </ul>
      </aside>

      {/* Main pane: Formal intake document */}
      <main className="msme-search-main">
        <header className="credit-file-header">
          <h1>Credit Assessment Request</h1>
          <p>Complete all required fields to initiate financial health score computation from registered data sources.</p>
        </header>

        {error && (
          <ErrorMessage
            message={error.message}
            severity={error.severity}
            onRetry={error.retryable ? handleRetry : null}
            title="Assessment Failed"
            details={error.technical}
          />
        )}

        {loading && (
          <div className="loading-container">
            <LoadingSpinner 
              size="large" 
              message="Aggregating data from GST, UPI, Account Aggregator, and EPFO sources..." 
            />
          </div>
        )}

        {!loading && (
          <form onSubmit={handleSubmit}>
            {/* Basic Information */}
            <section className="form-section">
              <h2 className="section-header">I. Basic Information</h2>
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="msmeId">
                    MSME Identifier <span className="required-mark">*</span>
                  </label>
                  <input
                    id="msmeId"
                    type="text"
                    data-type="code"
                    value={msmeId}
                    onChange={(e) => setMsmeId(e.target.value)}
                    required
                    placeholder="MSME-2024-001"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="sector">
                    Business Sector <span className="required-mark">*</span>
                  </label>
                  <select
                    id="sector"
                    value={sector}
                    onChange={(e) => setSector(e.target.value)}
                    required
                  >
                    <option value="Trader">Trader</option>
                    <option value="Manufacturer">Manufacturer</option>
                    <option value="Services">Services</option>
                  </select>
                </div>
              </div>
            </section>

            {/* Data Source Identifiers */}
            <section className="form-section">
              <h2 className="section-header">II. Data Source Identifiers</h2>
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="gstNumber">
                    GST Registration Number <span className="required-mark">*</span>
                  </label>
                  <input
                    id="gstNumber"
                    type="text"
                    data-type="code"
                    value={gstNumber}
                    onChange={(e) => setGstNumber(e.target.value)}
                    required
                    placeholder="29ABCDE1234F1Z5"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="upiId">
                    UPI Identifier <span className="required-mark">*</span>
                  </label>
                  <input
                    id="upiId"
                    type="text"
                    data-type="code"
                    value={upiId}
                    onChange={(e) => setUpiId(e.target.value)}
                    required
                    placeholder="business@bank"
                  />
                </div>
              </div>
            </section>

            {/* Financial Data Access */}
            <section className="form-section">
              <h2 className="section-header">III. Financial Data Access</h2>
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="aaConsentToken">
                    Account Aggregator Consent Token <span className="required-mark">*</span>
                  </label>
                  <input
                    id="aaConsentToken"
                    type="text"
                    data-type="code"
                    value={aaConsentToken}
                    onChange={(e) => setAaConsentToken(e.target.value)}
                    required
                    placeholder="AA-CONSENT-XYZ123"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="epfoEstablishmentId">
                    EPFO Establishment ID <span className="required-mark">*</span>
                  </label>
                  <input
                    id="epfoEstablishmentId"
                    type="text"
                    data-type="code"
                    value={epfoEstablishmentId}
                    onChange={(e) => setEpfoEstablishmentId(e.target.value)}
                    required
                    placeholder="EPFO-EST-12345"
                  />
                </div>
              </div>
            </section>

            <div className="submit-actions">
              <button type="submit" disabled={loading} className="btn-submit-assessment">
                {loading ? 'Processing Assessment...' : 'Initiate Credit Assessment'}
              </button>
              {loading && (
                <p className="loading-note">
                  Retrieving and analyzing data from all registered sources...
                </p>
              )}
            </div>
          </form>
        )}
      </main>
    </div>
  )
}

export default MSMESearch
