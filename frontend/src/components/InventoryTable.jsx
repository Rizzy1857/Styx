import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { formatDate, formatScore } from '../utils/formatters'

export default function InventoryTable({ apis }) {
  const navigate = useNavigate()
  const [sortBy, setSortBy] = useState('endpoint')
  const [sortOrder, setSortOrder] = useState('asc')
  const [filterStatus, setFilterStatus] = useState('')

  const sorted = useMemo(() => {
    let data = [...apis]
    if (filterStatus) {
      data = data.filter((api) => api.current_status === filterStatus)
    }

    return data.sort((a, b) => {
      let aVal, bVal
      switch (sortBy) {
        case 'endpoint':
          aVal = a.endpoint || ''
          bVal = b.endpoint || ''
          break
        case 'status':
          aVal = a.current_status || ''
          bVal = b.current_status || ''
          break
        case 'zombie_score':
          aVal = a.zombie_score || 0
          bVal = b.zombie_score || 0
          break
        case 'last_traffic_seen':
          aVal = new Date(a.last_traffic_seen || 0).getTime()
          bVal = new Date(b.last_traffic_seen || 0).getTime()
          break
        default:
          aVal = a.endpoint || ''
          bVal = b.endpoint || ''
      }

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1
      return 0
    })
  }, [apis, sortBy, sortOrder, filterStatus])

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(column)
      setSortOrder('asc')
    }
  }

  const statuses = [...new Set(apis.map((a) => a.current_status))].filter(Boolean)

  const StatusBadge = ({ status }) => {
    const colorClass = {
      ACTIVE: 'bg-green-900 text-green-200',
      DEPRECATED: 'bg-yellow-900 text-yellow-200',
      ZOMBIE: 'bg-red-900 text-red-200',
      SHADOW: 'bg-purple-900 text-purple-200',
    }[status]

    return (
      <span
        className={`px-3 py-1 rounded-full text-sm font-medium ${colorClass || 'bg-gray-900 text-gray-200'}`}
      >
        {status}
      </span>
    )
  }

  const SortIcon = ({ column }) => {
    if (sortBy !== column) return <span className="text-ice-blue/30 ml-2">⇅</span>
    return <span className="text-ice-blue ml-2">{sortOrder === 'asc' ? '↑' : '↓'}</span>
  }

  return (
    <div className="space-y-4">
      {/* Filter Bar */}
      <div className="px-6 pt-6 pb-4 border-b border-light-navy/30">
        <div className="flex items-center space-x-4">
          <label className="text-ice-blue/70 text-sm font-medium">Filter by Status:</label>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="bg-navy border border-light-navy/50 text-ice-blue px-3 py-2 rounded text-sm focus:outline-none focus:border-ice-blue/50"
          >
            <option value="">All Statuses</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
          <div className="text-ice-blue/50 text-sm ml-auto">
            Showing {sorted.length} of {apis.length}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-navy/50 border-b border-light-navy/30">
            <tr>
              <th
                className="px-6 py-3 text-left text-ice-blue font-semibold cursor-pointer hover:bg-light-navy/20"
                onClick={() => handleSort('endpoint')}
              >
                Endpoint <SortIcon column="endpoint" />
              </th>
              <th className="px-6 py-3 text-left text-ice-blue font-semibold">Method</th>
              <th
                className="px-6 py-3 text-left text-ice-blue font-semibold cursor-pointer hover:bg-light-navy/20"
                onClick={() => handleSort('status')}
              >
                Status <SortIcon column="status" />
              </th>
              <th
                className="px-6 py-3 text-left text-ice-blue font-semibold cursor-pointer hover:bg-light-navy/20"
                onClick={() => handleSort('zombie_score')}
              >
                Zombie Score <SortIcon column="zombie_score" />
              </th>
              <th
                className="px-6 py-3 text-left text-ice-blue font-semibold cursor-pointer hover:bg-light-navy/20"
                onClick={() => handleSort('last_traffic_seen')}
              >
                Last Seen <SortIcon column="last_traffic_seen" />
              </th>
              <th className="px-6 py-3 text-left text-ice-blue font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-light-navy/20">
            {sorted.length > 0 ? (
              sorted.map((api) => (
                <tr
                  key={api.id}
                  className="hover:bg-light-navy/10 transition cursor-pointer"
                  onClick={() => navigate(`/inventory/${api.id}`)}
                >
                  <td className="px-6 py-4 text-ice-blue font-mono text-xs">{api.endpoint}</td>
                  <td className="px-6 py-4 text-ice-blue">{api.method}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={api.current_status} />
                  </td>
                  <td className="px-6 py-4 text-ice-blue">{formatScore(api.zombie_score)}</td>
                  <td className="px-6 py-4 text-ice-blue/70 text-sm">
                    {formatDate(api.last_traffic_seen)}
                  </td>
                  <td className="px-6 py-4">
                    <button
                      type="button"
                      className="text-ice-blue hover:text-ice-blue/50 transition text-sm"
                      onClick={(event) => {
                        event.stopPropagation()
                        navigate(`/inventory/${api.id}`)
                      }}
                    >
                      Details →
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="px-6 py-8 text-center text-ice-blue/50">
                  No APIs found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
