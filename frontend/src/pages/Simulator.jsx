import React, { useState, useEffect } from 'react'
import { getAPIs, simulateBlastRadius } from '../services/api'
import BlastRadiusSimulator from '../components/BlastRadiusSimulator'

export default function Simulator() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [apis, setApis] = useState([])

  useEffect(() => {
    const fetchAPIs = async () => {
      try {
        const response = await getAPIs()
        setApis(response.data || [])
        setError(null)
      } catch (err) {
        setError(err.message || 'Failed to fetch APIs')
      } finally {
        setLoading(false)
      }
    }

    fetchAPIs()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-ice-blue">
          <div className="animate-spin text-3xl mb-4">⏳</div>
          <p>Loading simulator...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-700 rounded-lg p-4 text-red-200">
        <p className="font-semibold">Error</p>
        <p className="text-sm">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-ice-blue mb-2">Blast Radius Simulator</h1>
        <p className="text-ice-blue/70">Simulate the impact of decommissioning APIs</p>
      </div>

      <div className="bg-light-navy/20 border border-light-navy/50 rounded-lg overflow-hidden">
        <BlastRadiusSimulator apis={apis} onSimulate={simulateBlastRadius} />
      </div>
    </div>
  )
}
