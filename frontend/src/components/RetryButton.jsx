import React from 'react'
import { RotateCw } from 'lucide-react'
import './RetryButton.css'

const RetryButton = ({ 
  onRetry, 
  loading = false, 
  message = 'Retry',
  size = 'medium',
  variant = 'secondary'
}) => {
  return (
    <button 
      className={`retry-button btn-${variant} btn-${size}`}
      onClick={onRetry}
      disabled={loading}
    >
      <RotateCw 
        size={size === 'small' ? 16 : 20} 
        className={loading ? 'spinning' : ''} 
      />
      {message}
    </button>
  )
}

export default RetryButton
