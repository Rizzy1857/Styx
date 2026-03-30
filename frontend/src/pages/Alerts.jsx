import React, { useState, useEffect } from 'react'
import { getAlerts, acknowledgeAlert } from '../services/api'
import AlertsFeed from '../components/AlertsFeed'

export default function Alerts() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await getAlerts()
        setAlerts(response.data || [])
        setError(null)
      } catch (err) {
        setError(err.message || 'Failed to fetch alerts')
      } finally {
        setLoading(false)
      }
    }

    fetchAlerts()

    // Poll every 5 seconds
    const interval = setInterval(fetchAlerts, 5000)
    return () => clearInterval(interval)
  }, [])

  const handleAcknowledge = async (alertId) => {
    try {
      await acknowledgeAlert(alertId)
      setAlerts((prev) => prev.map((a) => (a.id === alertId ? { ...a, acknowledged: true } : a)))
    } catch (err) {
      console.error('Failed to acknowledge alert:', err)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-ice-blue">
          <div className="animate-spin text-3xl mb-4">⏳</div>
          <p>Loading alerts...</p>
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
        <h1 className="text-3xl font-bold text-ice-blue mb-2">Alerts</h1>
        <p className="text-ice-blue/70">API lifecycle and security events</p>
      </div>

      <AlertsFeed alerts={alerts} onAcknowledge={handleAcknowledge} />
    </div>
  )
}
