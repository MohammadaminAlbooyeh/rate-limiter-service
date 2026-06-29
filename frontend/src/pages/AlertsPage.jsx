import React from 'react';
import ThresholdAlert from '../components/ThresholdAlert';

function AlertsPage({ alerts, onRefresh }) {
  return (
    <div>
      <div className="header-container">
        <h1 className="header-title">Alerts</h1>
        <p className="header-subtitle">Threshold-based alerts when rate limit usage exceeds 90%.</p>
      </div>

      <div className="card">
        {(alerts || []).length === 0 && (
          <p style={{ color: 'var(--text-secondary)' }}>No alerts triggered yet.</p>
        )}
        {(alerts || []).map((alert, i) => (
          <ThresholdAlert key={i} alert={alert} />
        ))}
      </div>
    </div>
  );
}

export default AlertsPage;
