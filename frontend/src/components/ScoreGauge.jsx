import React from 'react'
import './ScoreGauge.css'

/**
 * Custom SVG semi-circular gauge component for displaying score 0-100
 * Color zones: Red (0-39), Yellow (40-69), Green (70-100)
 * With animated needle pointing to current score
 */
const ScoreGauge = ({ score, size = 300 }) => {
  // Validate score
  const validScore = Math.max(0, Math.min(100, score || 0))
  
  // Calculate dimensions
  const center = size / 2
  const radius = size * 0.35
  const strokeWidth = size * 0.08
  
  // Calculate arc path for semi-circle
  const startAngle = -180
  const endAngle = 0
  
  // Helper function to convert angle to radians
  const toRadians = (angle) => (angle * Math.PI) / 180
  
  // Helper function to calculate arc path
  const describeArc = (startAngle, endAngle) => {
    const start = polarToCartesian(center, center, radius, endAngle)
    const end = polarToCartesian(center, center, radius, startAngle)
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1'
    
    return [
      'M', start.x, start.y,
      'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y
    ].join(' ')
  }
  
  // Convert polar coordinates to cartesian
  const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
    const angleInRadians = toRadians(angleInDegrees)
    return {
      x: centerX + radius * Math.cos(angleInRadians),
      y: centerY + radius * Math.sin(angleInRadians)
    }
  }
  
  // Calculate needle angle (-180 to 0 degrees)
  const needleAngle = -180 + (validScore / 100) * 180
  const needleEnd = polarToCartesian(center, center, radius - strokeWidth / 2, needleAngle)
  
  // Determine risk zone color
  const getRiskColor = () => {
    if (validScore >= 70) return 'var(--risk-low)'
    if (validScore >= 40) return 'var(--risk-medium)'
    return 'var(--risk-high)'
  }
  
  // Create color zones
  const zones = [
    { start: -180, end: -108, color: 'var(--risk-high)' }, // 0-39: Red
    { start: -108, end: -36, color: 'var(--risk-medium)' }, // 40-69: Yellow
    { start: -36, end: 0, color: 'var(--risk-low)' }        // 70-100: Green
  ]
  
  return (
    <div className="score-gauge" style={{ width: size, height: size * 0.6 }}>
      <svg width={size} height={size * 0.6} viewBox={`0 0 ${size} ${size * 0.6}`}>
        {/* Background arc zones */}
        {zones.map((zone, idx) => (
          <path
            key={idx}
            d={describeArc(zone.start, zone.end)}
            fill="none"
            stroke={zone.color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            opacity="0.3"
          />
        ))}
        
        {/* Active arc showing current score */}
        <path
          d={describeArc(-180, needleAngle)}
          fill="none"
          stroke={getRiskColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          className="gauge-active-arc"
        />
        
        {/* Center pivot point */}
        <circle
          cx={center}
          cy={center}
          r={size * 0.03}
          fill={getRiskColor()}
        />
        
        {/* Needle */}
        <line
          x1={center}
          y1={center}
          x2={needleEnd.x}
          y2={needleEnd.y}
          stroke={getRiskColor()}
          strokeWidth={size * 0.012}
          strokeLinecap="round"
          className="gauge-needle"
        />
        
        {/* Score labels */}
        <text
          x={center * 0.15}
          y={center + 5}
          textAnchor="middle"
          className="gauge-label"
          style={{ fontSize: size * 0.06 }}
        >
          0
        </text>
        <text
          x={size * 0.85}
          y={center + 5}
          textAnchor="middle"
          className="gauge-label"
          style={{ fontSize: size * 0.06 }}
        >
          100
        </text>
      </svg>
      
      {/* Score display */}
      <div className="gauge-score-display">
        <div className="gauge-score" style={{ fontSize: size * 0.16 }}>
          {validScore.toFixed(1)}
        </div>
        <div className="gauge-score-label" style={{ fontSize: size * 0.05 }}>
          Financial Health Score
        </div>
      </div>
    </div>
  )
}

export default ScoreGauge
