import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ComposedChart
} from 'recharts';
import api from '../services/api';

export default function Analytics() {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        // First train model
        await api.post('/api/v1/analytics/train-model');
        // Then get overview
        const response = await api.get('/api/v1/analytics/overview');
        setOverview(response.data);
        setError(null);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load analytics');
        console.error('Analytics error:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
        {error}
      </div>
    );
  }

  if (!overview) return null;

  const {
    zombie_trend,
    distribution,
    risk_heatmap,
    top_at_risk,
    ml_model_metrics
  } = overview;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-gradient-to-r from-navy to-blue-700 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">Analytics Dashboard</h1>
        <p className="text-blue-100">Phase 2.1: ML-Powered API Intelligence</p>
      </div>

      {/* ML Model Status */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-600">Model Type</div>
          <div className="text-lg font-bold">{ml_model_metrics.model_type}</div>
        </div>
        <div className={`rounded-lg border p-4 ${ml_model_metrics.is_trained ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
          <div className="text-sm text-gray-600">Training Status</div>
          <div className="text-lg font-bold">{ml_model_metrics.is_trained ? '✓ Trained' : 'Not Trained'}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-600">Training Samples</div>
          <div className="text-lg font-bold">{ml_model_metrics.training_samples}</div>
        </div>
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="text-sm text-gray-600">Features</div>
          <div className="text-lg font-bold">{ml_model_metrics.features_count}</div>
        </div>
      </div>

      {/* Zombie Trend */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold">Zombie API Trend (30 Days)</h2>
          <p className="text-sm text-gray-600">Trend Direction: <span className={zombie_trend.trend_direction === 'increasing' ? 'text-red-600 font-bold' : zombie_trend.trend_direction === 'decreasing' ? 'text-green-600 font-bold' : 'text-gray-600'}>{zombie_trend.trend_direction}</span></p>
        </div>
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={zombie_trend.trend_data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="zombie_count" stroke="#ef4444" strokeWidth={2} name="Zombies" />
            <Line type="monotone" dataKey="active_count" stroke="#10b981" strokeWidth={2} name="Active" />
            <Line type="monotone" dataKey="deprecated_count" stroke="#f59e0b" strokeWidth={2} name="Deprecated" />
          </ComposedChart>
        </ResponsiveContainer>
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <div className="text-2xl font-bold text-red-600">{zombie_trend.current_zombie_count}</div>
          <div className="text-sm text-gray-600">{zombie_trend.zombie_percentage.toFixed(1)}% of all APIs are zombies</div>
        </div>
      </div>

      {/* API Distribution */}
      <div className="grid grid-cols-2 gap-6">
        {/* Status Distribution */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-xl font-bold mb-4">APIs by Status</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart
              data={Object.entries(distribution.by_status).map(([status, count]) => ({
                status, count
              }))}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="status" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6">
                {Object.entries(distribution.by_status).map(([status]) => (
                  <Cell
                    key={status}
                    fill={status === 'ACTIVE' ? '#10b981' : status === 'DEPRECATED' ? '#f59e0b' : status === 'ZOMBIE' ? '#ef4444' : '#6b7280'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Lifecycle Risk Distribution */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-xl font-bold mb-4">Lifecycle Risk Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={distribution.by_lifecycle_risk}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="bucket_name" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk Heatmap */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-bold mb-4">Risk Matrix Heatmap</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">Lifecycle vs Security</th>
                <th className="p-2">0-33% (Low)</th>
                <th className="p-2">33-67% (Medium)</th>
                <th className="p-2">67-100% (High)</th>
              </tr>
            </thead>
            <tbody>
              {['0-33', '33-67', '67-100'].map(lifecycle => (
                <tr key={lifecycle} className="border-b">
                  <td className="font-bold p-2">{lifecycle}% Lifecycle</td>
                  {['0-33', '33-67', '67-100'].map(security => {
                    const cell = risk_heatmap.heatmap.find(
                      c => c.lifecycle_bin === lifecycle && c.security_bin === security
                    );
                    const intensity = cell ? (cell.api_count / risk_heatmap.max_count) : 0;
                    const bgColor = intensity > 0.7 ? 'bg-red-400' : intensity > 0.4 ? 'bg-orange-300' : intensity > 0.1 ? 'bg-yellow-200' : 'bg-gray-100';
                    return (
                      <td key={`${lifecycle}-${security}`} className={`p-2 text-center font-bold ${bgColor}`}>
                        {cell?.api_count || 0}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Top At-Risk APIs */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-bold mb-4">Top {top_at_risk.top_apis.length} At-Risk APIs</h2>
        <div className="space-y-3">
          {top_at_risk.top_apis.map((api, idx) => (
            <div key={api.api_id} className="flex items-center justify-between p-3 border rounded hover:bg-gray-50">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="bg-gray-200 text-gray-700 text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <span className="font-mono text-sm">{api.endpoint}</span>
                  {api.has_anomalies && (
                    <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded">
                      ⚠️ Anomalies
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-600 mt-1">
                  Lifecycle: {(api.zombie_score * 100).toFixed(0)}% | Security: {(api.security_risk * 100).toFixed(0)}%
                </div>
              </div>
              <div className="text-right">
                <div className={`text-xl font-bold ${api.combined_risk > 0.7 ? 'text-red-600' : api.combined_risk > 0.5 ? 'text-orange-600' : 'text-yellow-600'}`}>
                  {(api.combined_risk * 100).toFixed(0)}%
                </div>
                <div className="w-32 bg-gray-200 rounded-full h-2 mt-1">
                  <div
                    className={`h-2 rounded-full ${api.combined_risk > 0.7 ? 'bg-red-600' : api.combined_risk > 0.5 ? 'bg-orange-600' : 'bg-yellow-600'}`}
                    style={{ width: `${api.combined_risk * 100}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm">
          <strong>{top_at_risk.critical_count}</strong> APIs have critical combined risk ({'>'}70%)
        </div>
      </div>

      {/* Security Risk Distribution */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-bold mb-4">Security Risk Distribution</h2>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={distribution.by_security_risk}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="bucket_name" angle={-45} textAnchor="end" height={80} />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#ef4444">
              {distribution.by_security_risk.map((item, idx) => (
                <Cell key={idx} fill={['#10b981', '#f59e0b', '#f97316', '#ef4444'][idx]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
