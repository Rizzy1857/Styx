import React, { useState } from 'react'

export default function SecurityFindings({ findings = [] }) {
  const [expanded, setExpanded] = useState({})

  const severityClass = (severity) => {
    if (severity === 'CRITICAL') return 'bg-red-900/30 text-red-200 border-red-700'
    if (severity === 'HIGH') return 'bg-orange-900/30 text-orange-200 border-orange-700'
    if (severity === 'MEDIUM') return 'bg-yellow-900/30 text-yellow-200 border-yellow-700'
    return 'bg-green-900/30 text-green-200 border-green-700'
  }

  if (!findings.length) {
    return <div className="bg-navy/30 border border-light-navy/40 rounded-lg p-4 text-ice-blue/60">No findings.</div>
  }

  return (
    <div className="space-y-3">
      {findings.map((finding, index) => {
        const isOpen = !!expanded[index]
        return (
          <div key={`${finding.category}-${index}`} className="bg-navy/30 border border-light-navy/40 rounded-lg p-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-ice-blue font-semibold">{finding.category}</p>
                <p className="text-ice-blue/60 text-sm">CVSS: {finding.cvss_score}</p>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 border rounded text-xs ${severityClass(finding.severity)}`}>{finding.severity}</span>
                <button
                  onClick={() => setExpanded((prev) => ({ ...prev, [index]: !isOpen }))}
                  className="text-sm text-ice-blue/80 hover:text-ice-blue"
                >
                  {isOpen ? 'Hide' : 'Details'}
                </button>
              </div>
            </div>
            {isOpen && <p className="text-ice-blue/70 text-sm mt-3">{finding.description}</p>}
          </div>
        )
      })}
    </div>
  )
}
