import React from 'react'
import './RiskStamp.css'

/**
 * Rotated ink-stamp seal showing risk assessment
 * Signature visual element with imperfect edges
 */
const RiskStamp = ({ riskBand }) => {
  const stampConfig = {
    Low: {
      color: '#1F9D6D',
      text: 'LOW RISK',
      rotation: -8
    },
    Medium: {
      color: '#C98A2C',
      text: 'MEDIUM RISK',
      rotation: 6
    },
    High: {
      color: '#A23B2E',
      text: 'HIGH RISK',
      rotation: -5
    }
  }

  const config = stampConfig[riskBand] || stampConfig.Medium

  return (
    <div 
      className="risk-stamp" 
      style={{ 
        '--stamp-color': config.color,
        '--stamp-rotation': `${config.rotation}deg`
      }}
    >
      <div className="stamp-outer-ring">
        <div className="stamp-inner-content">
          <div className="stamp-text-top">CREDIT ASSESSMENT</div>
          <div className="stamp-risk-band">{config.text}</div>
          <div className="stamp-text-bottom">VERIFIED</div>
        </div>
      </div>
    </div>
  )
}

export default RiskStamp
