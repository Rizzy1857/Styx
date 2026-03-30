import React from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

export default function AlertDetail({ alert }) {
  if (!alert) return null

  const triggerList = alert.trigger_metadata?.triggers || []
  const sourceIps = alert.trigger_metadata?.source_ips || []
  const userAgents = alert.trigger_metadata?.user_agents || []

  const series = triggerList.map((name, idx) => ({
    name,
    count: idx + 1,
  }))

  return (
    <div className="mt-4 bg-dark-navy border border-light-navy/40 rounded-lg p-4 space-y-4">
      <div>
        <p className="text-ice-blue font-semibold">Recommended Actions</p>
        <ul className="text-ice-blue/70 text-sm mt-2 space-y-1 list-disc list-inside">
          <li>Block unknown source IP ranges at the edge gateway.</li>
          <li>Enable strict authentication and token validation.</li>
          <li>Apply temporary rate limiting and monitor burst traffic.</li>
        </ul>
      </div>

      <div>
        <p className="text-ice-blue font-semibold mb-2">Trigger Timeline</p>
        <div className="h-36">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={series}>
              <XAxis dataKey="name" stroke="#CADCFC" tick={{ fontSize: 10 }} />
              <YAxis stroke="#CADCFC" tick={{ fontSize: 10 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#93C5FD" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p className="text-ice-blue font-semibold">Source IPs</p>
          <div className="mt-2 space-y-1 max-h-24 overflow-y-auto">
            {sourceIps.length ? sourceIps.map((ip) => <p key={ip} className="text-xs text-ice-blue/70 font-mono">{ip}</p>) : <p className="text-xs text-ice-blue/50">No IP data</p>}
          </div>
        </div>
        <div>
          <p className="text-ice-blue font-semibold">User Agents</p>
          <div className="mt-2 space-y-1 max-h-24 overflow-y-auto">
            {userAgents.length ? userAgents.map((ua, i) => <p key={`${ua}-${i}`} className="text-xs text-ice-blue/70 truncate">{ua || '<empty>'}</p>) : <p className="text-xs text-ice-blue/50">No UA data</p>}
          </div>
        </div>
      </div>
    </div>
  )
}
