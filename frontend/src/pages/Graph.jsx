import React, { useState, useEffect } from 'react'
import { getAPIs, getAPIDependencies } from '../services/api'
import DependencyGraph from '../components/DependencyGraph'

export default function Graph() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [apis, setApis] = useState([])
  const [selectedApi, setSelectedApi] = useState(null)
  const [graphData, setGraphData] = useState(null)

  useEffect(() => {
    const fetchAPIs = async () => {
      try {
        const response = await getAPIs()
        const apisData = response.data || []
        setApis(apisData)
        if (apisData.length > 0) {
          setSelectedApi(apisData[0].id)
        }
        setError(null)
      } catch (err) {
        setError(err.message || 'Failed to fetch APIs')
      } finally {
        setLoading(false)
      }
    }

    fetchAPIs()
  }, [])

  useEffect(() => {
    if (!selectedApi) return

    const fetchGraph = async () => {
      try {
        const response = await getAPIDependencies(selectedApi)
        setGraphData(response.data)
      } catch (err) {
        console.warn(`Failed to fetch graph data: ${err.message}`)
      }
    }

    fetchGraph()
  }, [selectedApi])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-ice-blue">
          <div className="animate-spin text-3xl mb-4">⏳</div>
          <p>Loading dependencies...</p>
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
        <h1 className="text-3xl font-bold text-ice-blue mb-2">Dependency Graph</h1>
        <p className="text-ice-blue/70">Visualize API service dependencies</p>
      </div>

      <div className="bg-light-navy/20 border border-light-navy/50 rounded-lg p-4">
        <label className="text-ice-blue/70 text-sm font-medium block mb-3">Select API:</label>
        <select
          value={selectedApi || ''}
          onChange={(e) => setSelectedApi(e.target.value)}
          className="w-full bg-navy border border-light-navy/50 text-ice-blue px-4 py-2 rounded text-sm focus:outline-none focus:border-ice-blue/50 mb-6"
        >
          {apis.map((api) => (
            <option key={api.id} value={api.id}>
              {api.endpoint}
            </option>
          ))}
        </select>

        {graphData ? (
          <DependencyGraph data={graphData} />
        ) : (
          <div className="text-center text-ice-blue/50 py-8">Loading graph...</div>
        )}
      </div>
    </div>
  )
}
