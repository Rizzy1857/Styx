import React from 'react'

const WEIGHTS = {
  traffic_decay: 35,
  documentation: 25,
  auth_weakness: 20,
  dependency_orphan: 20,
}

const LABELS = {
  traffic_decay: 'Traffic Decay',
  documentation: 'Documentation Gap',
  auth_weakness: 'Auth Weakness',
  dependency_orphan: 'Dependency Orphan',
}

export default function ExplanationCard({ zombieScore, factors, classification }) {
  const items = Object.entries(factors || {})
  const ordered = items.sort((a, b) => b[1] - a[1])

  return (
    <div className="bg-navy/30 border border-light-navy/40 rounded-lg p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-ice-blue">Lifecycle Score Breakdown</h3>
        <div className="text-right">
          <p className="text-3xl font-bold text-ice-blue">{Math.round((zombieScore || 0) * 100)}%</p>
          <span className="px-2 py-1 rounded text-xs bg-light-navy text-ice-blue">{classification || 'UNKNOWN'}</span>
        </div>
      </div>

      {ordered.map(([key, value]) => {
        const contribution = (value || 0) * (WEIGHTS[key] || 0)
        return (
          <div key={key} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="text-ice-blue/80">{LABELS[key] || key}</span>
              <span className="text-ice-blue/60">{contribution.toFixed(1)} pts</span>
            </div>
            <div className="w-full bg-dark-navy rounded h-2 overflow-hidden">
              <div className="h-2 bg-ice-blue" style={{ width: `${Math.max(3, (value || 0) * 100)}%` }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}
