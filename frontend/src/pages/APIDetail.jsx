import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { getAPIDetails, getAPIScore } from '../services/api'
import ExplanationCard from '../components/ExplanationCard'
import SecurityFindings from '../components/SecurityFindings'

export default function APIDetail() {
  const { id } = useParams()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [api, setApi] = useState(null)
  const [score, setScore] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [apiRes, scoreRes] = await Promise.all([getAPIDetails(id), getAPIScore(id)])
        setApi(apiRes.data)
        setScore(scoreRes.data)
      } catch (err) {
        setError(err.message || 'Failed to load API details')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  if (loading) return <div className="text-ice-blue/70">Loading details...</div>
  if (error) return <div className="text-red-300">{error}</div>
  if (!api || !score) return <div className="text-ice-blue/70">No data found.</div>

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-ice-blue">{api.endpoint}</h1>
        <p className="text-ice-blue/70 text-sm">{api.method} • {api.current_status}</p>
      </div>

      <ExplanationCard
        zombieScore={score.lifecycle.zombie_score}
        factors={score.lifecycle.factors}
        classification={score.lifecycle.classification}
      />

      <div>
        <h2 className="text-lg font-semibold text-ice-blue mb-3">Security Findings</h2>
        <SecurityFindings findings={score.security.findings} />
      </div>
    </div>
  )
}
