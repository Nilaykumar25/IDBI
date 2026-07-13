import React from 'react'
import { Loader2 } from 'lucide-react'
import './LoadingSpinner.css'

const LoadingSpinner = ({ 
  size = 'medium', 
  message = 'Loading...', 
  fullScreen = false 
}) => {
  const sizeClass = `spinner-${size}`
  
  const spinner = (
    <div className={`loading-spinner ${sizeClass}`}>
      <Loader2 className="spinner-icon" />
      {message && <p className="spinner-message">{message}</p>}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="loading-fullscreen">
        {spinner}
      </div>
    )
  }

  return spinner
}

export default LoadingSpinner
