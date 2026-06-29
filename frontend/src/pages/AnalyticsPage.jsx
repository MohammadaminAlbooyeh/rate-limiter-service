import React from 'react';
import RequestChart from '../components/RequestChart';

function AnalyticsPage({ data, timeline, blockedLogs }) {
  return (
    <div>
      <div className="header-container">
        <h1 className="header-title">Analytics</h1>
        <p className="header-subtitle">Detailed usage statistics and request patterns.</p>
      </div>

      <div className="card">
        <h3 className="card-title">Request Timeline</h3>
        <RequestChart data={timeline || []} />
      </div>

      <div className="grid-3">
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <h3 className="card-title">Top Consumers</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 0.5rem' }}>Identity</th>
                <th style={{ textAlign: 'right', padding: '0.75rem 0.5rem' }}>Total Requests</th>
              </tr>
            </thead>
            <tbody>
              {(data || []).map((row, i) => (
                <tr key={i} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '0.5rem' }}>{row.identity}</td>
                  <td style={{ textAlign: 'right', padding: '0.5rem' }}>{row.total_requests}</td>
                </tr>
              ))}
              {(data || []).length === 0 && (
                <tr><td colSpan="2" style={{ padding: '1rem', color: 'var(--text-secondary)' }}>No data yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3 className="card-title">Recently Blocked</h3>
          <div className="list-container">
            {(blockedLogs || []).slice(0, 20).map((log, i) => (
              <div className="list-item" key={i} style={{ padding: '0.4rem 0.8rem' }}>
                <div>
                  <p className="list-item-title" style={{ fontSize: '0.85rem' }}>{log.identity}</p>
                  <p className="list-item-subtitle" style={{ fontSize: '0.75rem' }}>{log.method} {log.endpoint}</p>
                </div>
                <span className="badge danger">Blocked</span>
              </div>
            ))}
            {(blockedLogs || []).length === 0 && (
              <p style={{ color: 'var(--text-secondary)' }}>No blocked requests.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyticsPage;
