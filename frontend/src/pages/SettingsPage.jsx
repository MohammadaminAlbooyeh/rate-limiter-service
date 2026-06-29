import React from 'react';

function SettingsPage({ adminKey, onAdminKeyChange, onSaveAdminKey }) {
  const handleSubmit = (e) => {
    e.preventDefault();
    onSaveAdminKey();
    alert('Admin API key saved to localStorage.');
  };

  return (
    <div>
      <div className="header-container">
        <h1 className="header-title">Settings</h1>
        <p className="header-subtitle">Configure admin access and connection settings.</p>
      </div>

      <div className="card" style={{ maxWidth: '500px' }}>
        <h3 className="card-title">Admin API Key</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
          Required for rule management, whitelist/blacklist, and analytics endpoints when configured on the server.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">X-Admin-Key</label>
            <input className="form-control" type="password" value={adminKey}
              onChange={e => onAdminKeyChange(e.target.value)}
              placeholder="Enter your admin API key" />
          </div>
          <button className="btn" type="submit">Save Key</button>
        </form>
      </div>

      <div className="card" style={{ maxWidth: '500px', marginTop: '1rem' }}>
        <h3 className="card-title">API Endpoint</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          The frontend connects to <code>{process.env.REACT_APP_API_URL || '/api/v1'}</code>.
          Set <strong>REACT_APP_API_URL</strong> environment variable for custom backend URLs.
        </p>
      </div>
    </div>
  );
}

export default SettingsPage;
