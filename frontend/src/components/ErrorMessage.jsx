import React from 'react'
import { AlertCircle, XCircle, Info } from 'lucide-react'
import RetryButton from './RetryButton'
import './ErrorMessage.css'

const ErrorMessage = ({ 
  message, 
  type = 'error',
  severity = 'error', // 'error', 'warning', 'info'
  title = null,
  details = null,
  onDismiss = null,
  onRetry = null,
  className = '' 
}) => {
  // Support both 'type' and 'severity' props for backwards compatibility
  const effectiveSeverity = severity || type
  
  const severityClass = effectiveSeverity === 'warning' ? 'error-warning' : 
                        effectiveSeverity === 'info' ? 'error-info' : 
                        'error-danger'
  
  const Icon = effectiveSeverity === 'warning' ? AlertCircle : 
               effectiveSeverity === 'info' ? Info : 
               XCircle

  return (
    <div className={`error-message ${severityClass} ${className}`} role="alert">
      <Icon size={20} className="error-icon" />
      <div className="error-content">
        {title && <div className="error-title">{title}</div>}
        <div className="error-text">{message}</div>
        {details && <div className="error-details">{details}</div>}
        {onRetry && (
          <div className="error-actions">
            <RetryButton onRetry={onRetry} size="small" message="Try Again" />
          </div>
        )}
      </div>
      {onDismiss && (
        <button 
          className="error-dismiss" 
          onClick={onDismiss}
          aria-label="Dismiss error"
        >
          ×
        </button>
      )}
    </div>
  )
}

export default ErrorMessage
