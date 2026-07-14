import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Auth.css'

const Signup = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { signUp, signInWithGoogle, user, loading: authLoading } = useAuth()
  const navigate = useNavigate()

  // Redirect to dashboard if already logged in
  useEffect(() => {
    if (!authLoading && user) {
      console.log('User authenticated, redirecting to dashboard')
      navigate('/dashboard', { replace: true })
    }
  }, [user, authLoading, navigate])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (password !== confirmPassword) {
      return setError('Passwords do not match')
    }

    if (password.length < 6) {
      return setError('Password must be at least 6 characters')
    }

    setError('')
    setLoading(true)

    try {
      await signUp(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Failed to create account. Email may already exist.')
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignIn = async () => {
    setError('')
    setLoading(true)
    try {
      await signInWithGoogle()
      navigate('/dashboard')
    } catch (err) {
      setError(err.message || 'Failed to sign in with Google')
      setLoading(false)
    }
  }

  if (authLoading) {
    return null
  }

  return (
    <div className="auth-container">
      {/* Left branded panel */}
      <div className="auth-brand-panel">
        <div className="brand-content">
          <div className="brand-logo">
            <div className="brand-eyebrow">MSME Financial Health Score</div>
            <h1 className="brand-name">CreditLine</h1>
          </div>
          
          <div className="brand-tagline">
            <h2>Closing the MSME Credit Gap with Alternate Data</h2>
            <p>
              Traditional credit scoring leaves 63 million MSMEs underserved. CreditLine changes that.
            </p>
          </div>

          <div className="brand-features">
            <div className="feature-item">
              <div className="feature-icon">✓</div>
              <div className="feature-text">
                <strong>Alternate Data Scoring</strong>
                <span>GST, UPI, Account Aggregator, and EPFO data for comprehensive assessment</span>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">✓</div>
              <div className="feature-text">
                <strong>Dual-Layer Explainable AI</strong>
                <span>Composite weighted model + ML classifier with SHAP-based transparency</span>
              </div>
            </div>
            <div className="feature-item">
              <div className="feature-icon">✓</div>
              <div className="feature-text">
                <strong>Near Real-Time Assessment</strong>
                <span>Credit decisions in minutes, not weeks</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right form panel */}
      <div className="auth-form-panel">
        <div className="auth-card">
          <div className="auth-header">
            <h2>Create your account</h2>
          </div>
          {error && <div className="error-message">{error}</div>}
          <form onSubmit={handleSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                placeholder="you@example.com"
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="new-password"
                placeholder="••••••••"
                minLength={6}
              />
            </div>
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                autoComplete="new-password"
                placeholder="••••••••"
                minLength={6}
              />
            </div>
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </form>

          <div className="auth-divider">
            <span>or</span>
          </div>

          <button 
            type="button" 
            onClick={handleGoogleSignIn}
            className="btn btn-google"
            disabled={loading}
          >
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4"/>
              <path d="M9.003 18c2.43 0 4.467-.806 5.956-2.18L12.05 13.56c-.806.54-1.836.86-3.047.86-2.344 0-4.328-1.584-5.036-3.711H.96v2.332C2.44 15.983 5.485 18 9.003 18z" fill="#34A853"/>
              <path d="M3.964 10.712c-.18-.54-.282-1.117-.282-1.71 0-.593.102-1.17.282-1.71V4.96H.957C.347 6.175 0 7.55 0 9.002c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
              <path d="M9.003 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.464.891 11.428 0 9.002 0 5.485 0 2.44 2.017.96 4.958L3.967 7.29c.708-2.127 2.692-3.71 5.036-3.71z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </button>

          <div className="auth-footer">
            <p>
              Already have an account? <Link to="/login">Sign in</Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Signup
