import React, { useState } from 'react'

export default function BlastRadiusSimulator({ apis, onSimulate }) {
  const [selectedApis, setSelectedApis] = useState([])
  const [simulating, setSimulating] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleToggleApi = (apiId) => {
    setSelectedApis((prev) =>
      prev.includes(apiId) ? prev.filter((id) => id !== apiId) : [...prev, apiId]
    )
  }

  const handleSimulate = async () => {
    if (selectedApis.length === 0) {
      setError('Please select at least one API')
      return
    }

    setSimulating(true)
    setError(null)

    try {
      const response = await onSimulate(selectedApis)
      setResult(response.data)
    } catch (err) {
      setError(err.message || 'Simulation failed')
    } finally {
      setSimulating(false)
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'HIGH':
        return 'text-red-400 bg-red-900/20 border-red-700'
      case 'MEDIUM':
        return 'text-yellow-400 bg-yellow-900/20 border-yellow-700'
      default:
        return 'text-green-400 bg-green-900/20 border-green-700'
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
      {/* Left Panel - API Selection */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-ice-blue">Select APIs to Decommission</h3>
        <div className="max-h-96 overflow-y-auto space-y-2 bg-navy/20 border border-light-navy/30 rounded p-4">
          {apis.map((api) => (
            <label
              key={api.id}
              className="flex items-center space-x-3 p-3 hover:bg-light-navy/20 rounded cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedApis.includes(api.id)}
                onChange={() => handleToggleApi(api.id)}
                className="rounded border-light-navy/50 bg-navy text-ice-blue focus:ring-ice-blue"
              />
              <div className="flex-1">
                <p className="text-ice-blue font-mono text-sm">{api.endpoint}</p>
                <p className="text-ice-blue/50 text-xs">{api.method} • {api.current_status}</p>
              </div>
            </label>
          ))}
        </div>

        <button
          onClick={handleSimulate}
          disabled={simulating || selectedApis.length === 0}
          className="w-full px-4 py-3 bg-light-navy hover:bg-navy disabled:bg-gray-700 disabled:cursor-not-allowed rounded text-ice-blue font-semibold transition"
        >
          {simulating ? 'Simulating...' : `Simulate Decommission (${selectedApis.length})`}
        </button>
      </div>

      {/* Right Panel - Results */}
      <div className="space-y-4">
        <h3 className="text-xl font-semibold text-ice-blue">Impact Analysis</h3>

        {error && (
          <div className="bg-red-900/30 border border-red-700 rounded p-4 text-red-200">
            {error}
          </div>
        )}

        {!result && !error && (
          <div className="bg-navy/20 border border-light-navy/30 rounded p-8 text-center text-ice-blue/50">
            Select APIs and run simulation
          </div>
        )}

        {result && (
          <div className="space-y-4">
            {/* Severity Badge */}
            <div className={`border rounded p-4 ${getSeverityColor(result.severity)}`}>
              <p className="text-sm opacity-70 mb-1">Impact Severity</p>
              <p className="text-2xl font-bold">{result.severity}</p>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-navy/20 border border-light-navy/30 rounded p-4">
                <p className="text-ice-blue/70 text-sm">Dependent Services</p>
                <p className="text-2xl font-bold text-ice-blue">{result.dependent_services}</p>
              </div>
              <div className="bg-navy/20 border border-light-navy/30 rounded p-4">
                <p className="text-ice-blue/70 text-sm">Traffic Impact</p>
                <p className="text-2xl font-bold text-ice-blue">
                  {(result.traffic_percentage * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Impact Score */}
            <div className="bg-navy/20 border border-light-navy/30 rounded p-4">
              <p className="text-ice-blue/70 text-sm mb-2">Overall Impact Score</p>
              <div className="w-full bg-dark-navy rounded-full h-3 overflow-hidden">
                <div
                  className={`h-3 transition-all duration-500 ${
                    result.impact_score > 0.7
                      ? 'bg-red-500'
                      : result.impact_score > 0.3
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                  }`}
                  style={{ width: `${result.impact_score * 100}%` }}
                ></div>
              </div>
              <p className="text-ice-blue mt-2 font-semibold">{(result.impact_score * 100).toFixed(0)}%</p>
            </div>

            {/* Recommendation */}
            <div className="bg-light-navy/20 border border-light-navy/50 rounded p-4">
              <p className="text-ice-blue font-semibold mb-2">Recommendation</p>
              <p className="text-ice-blue/80">{result.recommendation}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
