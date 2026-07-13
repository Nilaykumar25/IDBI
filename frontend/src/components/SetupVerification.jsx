/**
 * Setup verification component.
 * Displays configuration status for debugging.
 */
import { useState, useEffect } from 'react'
import apiClient from '../lib/api'

const SetupVerification = () => {
  const [backendHealth, setBackendHealth] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    checkBackendHealth()
  }, [])

  const checkBackendHealth = async () => {
    try {
      const response = await apiClient.get('/health')
      setBackendHealth(response.data)
      setError(null)
    } catch (err) {
      setError(err.message)
      setBackendHealth(null)
    }
  }

  const supabaseConfigured = 
    import.meta.env.VITE_SUPABASE_URL && 
    import.meta.env.VITE_SUPABASE_ANON_KEY

  return (
    <div style={{ 
      padding: '2rem', 
      maxWidth: '600px', 
      margin: '0 auto',
      fontFamily: 'monospace',
      fontSize: '0.9rem'
    }}>
      <h3>🔧 Setup Verification</h3>
      
      <div style={{ marginTop: '1.5rem' }}>
        <h4>Frontend Configuration</h4>
        <div style={{ marginLeft: '1rem' }}>
          <div>
            {supabaseConfigured ? '✅' : '❌'} Supabase configured
          </div>
          <div>
            {import.meta.env.VITE_API_URL ? '✅' : '❌'} API URL configured
          </div>
        </div>
      </div>

      <div style={{ marginTop: '1.5rem' }}>
        <h4>Backend Health Check</h4>
        <div style={{ marginLeft: '1rem' }}>
          {backendHealth ? (
            <>
              <div>✅ Backend is reachable</div>
              <div>✅ Status: {backendHealth.status}</div>
              <div>✅ Adapter mode: {backendHealth.adapter_mode}</div>
            </>
          ) : error ? (
            <>
              <div>❌ Backend not reachable</div>
              <div style={{ color: 'red', fontSize: '0.8rem' }}>
                Error: {error}
              </div>
              <div style={{ marginTop: '0.5rem', fontSize: '0.8rem' }}>
                Make sure the backend is running on port 5000
              </div>
            </>
          ) : (
            <div>⏳ Checking...</div>
          )}
        </div>
      </div>

      {!supabaseConfigured && (
        <div style={{ 
          marginTop: '1.5rem', 
          padding: '1rem', 
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px'
        }}>
          <strong>⚠️ Configuration Incomplete</strong>
          <p style={{ marginTop: '0.5rem', fontSize: '0.85rem' }}>
            Create a <code>.env</code> file in the frontend directory 
            with your Supabase credentials. See <code>.env.example</code> for template.
          </p>
        </div>
      )}
    </div>
  )
}

export default SetupVerification
