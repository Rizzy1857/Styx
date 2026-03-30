/**
 * Formatting utilities for display
 */

export const formatDate = (timestamp) => {
  if (!timestamp) return 'Never'
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now - date
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffMinutes = Math.floor(diffMs / (1000 * 60))

  if (diffMinutes < 60) return `${diffMinutes}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 30) return `${diffDays}d ago`
  return date.toLocaleDateString()
}

export const formatScore = (score) => {
  if (score === undefined || score === null) return 'N/A'
  const percentage = Math.round(score * 100)
  let risk = 'Low'
  if (percentage > 70) risk = 'Critical'
  else if (percentage > 50) risk = 'High'
  else if (percentage > 30) risk = 'Medium'
  return `${percentage}% (${risk})`
}

export const formatStatus = (status) => {
  const statusMap = {
    ACTIVE: 'Active',
    DEPRECATED: 'Deprecated',
    ZOMBIE: 'Zombie',
    SHADOW: 'Shadow',
  }
  return statusMap[status] || status
}

export const getStatusColor = (status) => {
  const colorMap = {
    ACTIVE: 'green',
    DEPRECATED: 'yellow',
    ZOMBIE: 'red',
    SHADOW: 'purple',
  }
  return colorMap[status] || 'gray'
}

export const getSeverityColor = (severity) => {
  const colorMap = {
    CRITICAL: 'red',
    HIGH: 'orange',
    MEDIUM: 'yellow',
    LOW: 'green',
  }
  return colorMap[severity] || 'gray'
}

export const formatPercentage = (value) => {
  if (value === undefined || value === null) return 'N/A'
  return `${Math.round(value * 100)}%`
}
