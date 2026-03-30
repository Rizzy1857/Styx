import React, { useMemo } from 'react'

export default function SecurityMatrix({ apis, scores }) {
  const matrixData = useMemo(() => {
    return apis.map((api) => {
      const score = scores[api.id]
      return {
        id: api.id,
        endpoint: api.endpoint,
        lifecycle: score?.lifecycle?.zombie_score || 0,
        security: score?.security?.security_risk_score || 0,
        status: api.current_status,
      }
    })
  }, [apis, scores])

  const getQuadrantColor = (lifecycle, security) => {
    if (security > 0.6 && lifecycle > 0.6) return '#DC2626' // Red - High both
    if (security > 0.6) return '#F59E0B' // Orange - High security
    if (lifecycle > 0.6) return '#EAB308' // Yellow - High lifecycle
    return '#10B981' // Green - Low both
  }

  const getQuadrantLabel = (lifecycle, security) => {
    if (security > 0.6 && lifecycle > 0.6) return 'Critical Risk'
    if (security > 0.6) return 'Security Risk'
    if (lifecycle > 0.6) return 'Lifecycle Risk'
    return 'Healthy'
  }

  return (
    <div className="space-y-4">
      {/* Legend */}
      <div className="grid grid-cols-4 gap-4 mb-6 text-sm">
        {[
          { label: 'Critical Risk', color: '#DC2626' },
          { label: 'Security Risk', color: '#F59E0B' },
          { label: 'Lifecycle Risk', color: '#EAB308' },
          { label: 'Healthy', color: '#10B981' },
        ].map((item) => (
          <div key={item.label} className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }}></div>
            <span className="text-ice-blue/70">{item.label}</span>
          </div>
        ))}
      </div>

      {/* 2D Scatter Plot */}
      <svg width="100%" height="400" viewBox="0 0 600 400" className="border border-light-navy/30 rounded">
        {/* Axis lines */}
        <line x1="50" y1="350" x2="550" y2="350" stroke="#CADCFC" strokeWidth="2" opacity="0.3" />
        <line x1="50" y1="350" x2="50" y2="50" stroke="#CADCFC" strokeWidth="2" opacity="0.3" />

        {/* Grid lines */}
        {[0.25, 0.5, 0.75].map((v) => (
          <g key={`h-${v}`}>
            <line x1="50" y1={350 - v * 300} x2="550" y2={350 - v * 300} stroke="#CADCFC" strokeWidth="1" opacity="0.1" />
            <line x1={50 + v * 500} y1="50" x2={50 + v * 500} y2="350" stroke="#CADCFC" strokeWidth="1" opacity="0.1" />
          </g>
        ))}

        {/* Quadrant backgrounds */}
        <rect x="50" y="50" width="250" height="300" fill="#10B981" opacity="0.05" />
        <rect x="300" y="50" width="250" height="300" fill="#EAB308" opacity="0.05" />
        <rect x="50" y="200" width="250" height="150" fill="#F59E0B" opacity="0.05" />
        <rect x="300" y="200" width="250" height="150" fill="#DC2626" opacity="0.05" />

        {/* Axis labels */}
        <text x="300" y="380" textAnchor="middle" fill="#CADCFC" fontSize="12">
          Lifecycle Risk →
        </text>
        <text x="20" y="200" textAnchor="middle" fill="#CADCFC" fontSize="12" transform="rotate(-90 20 200)">
          Security Risk →
        </text>

        {/* Data points */}
        {matrixData.map((point) => {
          const x = 50 + point.lifecycle * 500
          const y = 350 - point.security * 300
          const color = getQuadrantColor(point.lifecycle, point.security)
          return (
            <circle
              key={point.id}
              cx={x}
              cy={y}
              r="6"
              fill={color}
              opacity="0.8"
              className="hover:r-8 transition cursor-pointer"
              title={`${point.endpoint}: ${point.status}`}
            />
          )
        })}
      </svg>

      {/* Summary Statistics */}
      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="bg-navy/30 border border-light-navy/30 rounded p-4">
          <p className="text-ice-blue/70 text-sm">Critical APIs</p>
          <p className="text-2xl font-bold text-ice-blue">
            {matrixData.filter((d) => d.lifecycle > 0.6 && d.security > 0.6).length}
          </p>
        </div>
        <div className="bg-navy/30 border border-light-navy/30 rounded p-4">
          <p className="text-ice-blue/70 text-sm">Healthy APIs</p>
          <p className="text-2xl font-bold text-green-400">
            {matrixData.filter((d) => d.lifecycle <= 0.4 && d.security <= 0.4).length}
          </p>
        </div>
        <div className="bg-navy/30 border border-light-navy/30 rounded p-4">
          <p className="text-ice-blue/70 text-sm">Total APIs</p>
          <p className="text-2xl font-bold text-ice-blue">{matrixData.length}</p>
        </div>
      </div>
    </div>
  )
}
