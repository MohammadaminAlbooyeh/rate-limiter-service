import React from 'react';
import RequestChart from '../components/RequestChart';
import BlockedIPList from '../components/BlockedIPList';

function DashboardPage({ stats, blockedLogs, topConsumers, timeline, simForm, simResult, onSimFormChange, onSimulate, onRefresh }) {
  const s = stats || { total_requests: 0, allowed_requests: 0, blocked_requests: 0 };

  return (
    <div>
      <div className="header-container">
        <h1 className="header-title">Dashboard</h1>
        <p className="header-subtitle">Real-time rate limiting overview and traffic insights.</p>
      </div>

      <div className="grid-4">
        <div className="card stat-card">
          <p className="stat-label">Total Requests</p>
          <p className="stat-value">{s.total_requests}</p>
        </div>
        <div className="card stat-card">
          <p className="stat-label">Allowed</p>
          <p className="stat-value" style={{ color: 'var(--success)' }}>{s.allowed_requests}</p>
        </div>
        <div className="card stat-card">
          <p className="stat-label">Blocked</p>
          <p className="stat-value" style={{ color: 'var(--danger)' }}>{s.blocked_requests}</p>
        </div>
        <div className="card stat-card">
          <p className="stat-label">Block Rate</p>
          <p className="stat-value" style={{ color: 'var(--warning)' }}>
            {s.total_requests > 0 ? ((s.blocked_requests / s.total_requests) * 100).toFixed(1) : 0}%
          </p>
        </div>
      </div>

      <div className="grid-3">
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <h3 className="card-title">Request Timeline (30 min)</h3>
          <RequestChart data={timeline || []} />
        </div>

        <div className="card">
          <h3 className="card-title">Test a Request</h3>
          <form onSubmit={onSimulate}>
            <div className="form-group">
              <label className="form-label">Client IP</label>
              <input className="form-control" type="text" value={simForm.ip}
                onChange={e => onSimFormChange({ ...simForm, ip: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">API Key</label>
              <input className="form-control" type="text" value={simForm.api_key}
                onChange={e => onSimFormChange({ ...simForm, api_key: e.target.value })} />
            </div>
            <div className="form-group">
              <label className="form-label">Endpoint</label>
              <input className="form-control" type="text" value={simForm.endpoint}
                onChange={e => onSimFormChange({ ...simForm, endpoint: e.target.value })} required />
            </div>
            <div className="form-group" style={{ margin: 0 }}>
              <label className="form-label">HTTP Method</label>
              <select className="form-control" value={simForm.method}
                onChange={e => onSimFormChange({ ...simForm, method: e.target.value })}>
                <option value="GET">GET</option>
                <option value="POST">POST</option>
                <option value="DELETE">DELETE</option>
              </select>
            </div>
            <button className="btn" type="submit">Send Test Request</button>
          </form>

          {simResult && (
            <div style={{ marginTop: '1.5rem', padding: '1rem', borderRadius: '8px',
              background: simResult.allowed ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
              border: `1px solid ${simResult.allowed ? 'var(--success)' : 'var(--danger)'}` }}>
              <strong>Response Status:</strong> {simResult.status} <br />
              <strong>Allowed:</strong> {simResult.allowed ? 'YES' : 'NO'} <br />
              <strong>Details:</strong> {simResult.detail} <br />
              {simResult.limit && <><strong>Rate Limit:</strong> {simResult.limit} <br /></>}
              {simResult.remaining && <><strong>Remaining:</strong> {simResult.remaining} <br /></>}
              {simResult.reset && <><strong>Reset In:</strong> {simResult.reset}s <br /></>}
              {simResult.algorithm && <><strong>Algorithm:</strong> {simResult.algorithm} <br /></>}
            </div>
          )}
        </div>
      </div>

      <div className="grid-3">
        <div className="card">
          <h3 className="card-title">Top Consumers</h3>
          <div className="list-container">
            {(topConsumers || []).map((consumer, index) => (
              <div className="list-item" key={index} style={{ padding: '0.5rem 1rem' }}>
                <span>{consumer.identity}</span>
                <span className="badge success">{consumer.total_requests} reqs</span>
              </div>
            ))}
            {(topConsumers || []).length === 0 &&
              <p style={{ color: 'var(--text-secondary)' }}>No request data available.</p>}
          </div>
        </div>

        <div className="card" style={{ gridColumn: 'span 2' }}>
          <h3 className="card-title">Recently Blocked Requests</h3>
          <div className="list-container">
            {(blockedLogs || []).map((log, index) => (
              <div className="list-item" key={index}>
                <div>
                  <p className="list-item-title">{log.identity}</p>
                  <p className="list-item-subtitle">{log.method} {log.endpoint} - {new Date(log.timestamp).toLocaleTimeString()}</p>
                </div>
                <span className="badge danger">Blocked</span>
              </div>
            ))}
            {(blockedLogs || []).length === 0 &&
              <p style={{ color: 'var(--text-secondary)' }}>No recently blocked requests.</p>}
          </div>
        </div>
      </div>

      <div className="card">
        <BlockedIPList />
      </div>
    </div>
  );
}

export default DashboardPage;
