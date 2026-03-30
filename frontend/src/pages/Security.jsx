import React, { useState, useEffect } from 'react'
import { getAPIs, getAPIScore } from '../services/api'
import SecurityMatrix from '../components/SecurityMatrix'

export default function Security() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [apis, setApis] = useState([])
  const [scores, setScores] = useState({})

  useEffect(() => {
    const fetchData = async () => {
      try {
        const apisResponse = await getAPIs()
        const apisData = apisResponse.data || []
        setApis(apisData)

        const scoreResults = await Promise.allSettled(
          apisData.map((api) => getAPIScore(api.id).then((response) => ({ id: api.id, data: response.data })))
        )
        const scoresMap = {}
        scoreResults.forEach((result) => {
          if (result.status === 'fulfilled') {
            scoresMap[result.value.id] = result.value.data
          }
        })
        setScores(scoresMap)
        setError(null)
      } catch (err) {
        setError(err.message || 'Failed to fetch data')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-ice-blue">
          <div className="animate-spin text-3xl mb-4">⏳</div>
          <p>Analyzing security...</p>
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
        <h1 className="text-3xl font-bold text-ice-blue mb-2">Security Analysis</h1>
        <p className="text-ice-blue/70">API security posture vs lifecycle risk</p>
      </div>

      <div className="bg-light-navy/20 border border-light-navy/50 rounded-lg overflow-hidden p-6">
        <SecurityMatrix apis={apis} scores={scores} />
      </div>
    </div>
  )
}
