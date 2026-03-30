import React from 'react'
import { formatDate } from '../utils/formatters'
import AlertDetail from './AlertDetail'

export default function AlertsFeed({ alerts, onAcknowledge }) {
  const [expandedAlertId, setExpandedAlertId] = React.useState(null)
  const getAlertIcon = (type) => {
    switch (type) {
      case 'ZOMBIE_RESURRECTION':
        return '🔄'
      case 'SHADOW_DISCOVERED':
        return '👻'
      case 'SECURITY_VIOLATION':
        return '⚠️'
      default:
        return '🔔'
    }
  }

  const getAlertTitle = (type) => {
    switch (type) {
      case 'ZOMBIE_RESURRECTION':
        return 'Zombie API Resurrection'
      case 'SHADOW_DISCOVERED':
        return 'Shadow API Discovered'
      case 'SECURITY_VIOLATION':
        return 'Security Violation'
      default:
        return 'Alert'
    }
  }

  const getSeverityClass = (severity) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-900/20 border-red-700'
      case 'HIGH':
        return 'bg-orange-900/20 border-orange-700'
      case 'MEDIUM':
        return 'bg-yellow-900/20 border-yellow-700'
      default:
        return 'bg-blue-900/20 border-blue-700'
    }
  }

  if (alerts.length === 0) {
    return (
      <div className="bg-light-navy/20 border border-light-navy/50 rounded-lg p-8 text-center text-ice-blue/50">
        No alerts
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`border rounded-lg p-4 transition ${getSeverityClass(alert.severity)} ${
            alert.acknowledged ? 'opacity-60' : ''
          }`}
        >
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <span className="text-2xl mt-1">{getAlertIcon(alert.alert_type)}</span>
              <div className="flex-1">
                <h3 className="font-semibold text-ice-blue">{getAlertTitle(alert.alert_type)}</h3>
                <p className="text-ice-blue/70 text-sm mt-1">
                  API ID: <span className="font-mono">{alert.api_id.substring(0, 8)}</span>
                </p>
                {alert.trigger_metadata?.triggers && (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {alert.trigger_metadata.triggers.map((trigger) => (
                      <span
                        key={trigger}
                        className="px-2 py-1 bg-navy/50 text-ice-blue/70 text-xs rounded font-mono"
                      >
                        {trigger}
                      </span>
                    ))}
                  </div>
                )}
                <p className="text-ice-blue/50 text-xs mt-2">{formatDate(alert.created_at)}</p>
              </div>
            </div>
            <div className="flex items-center space-x-3 ml-4">
              <span
                className={`px-3 py-1 rounded text-sm font-medium ${
                  alert.severity === 'CRITICAL'
                    ? 'bg-red-900 text-red-200'
                    : alert.severity === 'HIGH'
                      ? 'bg-orange-900 text-orange-200'
                      : 'bg-yellow-900 text-yellow-200'
                }`}
              >
                {alert.severity}
              </span>
              {!alert.acknowledged && (
                <button
                  onClick={() => onAcknowledge(alert.id)}
                  className="px-3 py-1 bg-light-navy hover:bg-navy rounded text-ice-blue text-sm transition"
                >
                  Ack
                </button>
              )}
              <button
                onClick={() =>
                  setExpandedAlertId((prev) => (prev === alert.id ? null : alert.id))
                }
                className="px-3 py-1 border border-light-navy/50 rounded text-ice-blue text-sm hover:bg-navy/30"
              >
                {expandedAlertId === alert.id ? 'Less' : 'More'}
              </button>
              {alert.acknowledged && <span className="text-ice-blue/50 text-sm">✓ Acknowledged</span>}
            </div>
          </div>
          {expandedAlertId === alert.id && <AlertDetail alert={alert} />}
        </div>
      ))}
    </div>
  )
}
