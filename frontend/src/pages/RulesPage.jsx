import React, { useState } from 'react';
import RuleCard from '../components/RuleCard';
import AlgorithmSelector from '../components/AlgorithmSelector';

function RulesPage({ rules, onRefresh, apiFetch }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', algorithm: 'fixed_window', limit: 100, window: 60, endpoint: '*', identity: 'ip' });

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await apiFetch('/api/v1/rules', {
        method: 'POST',
        body: JSON.stringify(form),
      });
      if (res.ok) {
        setForm({ name: '', algorithm: 'fixed_window', limit: 100, window: 60, endpoint: '*', identity: 'ip' });
        setShowForm(false);
        onRefresh();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (ruleId, ruleName) => {
    if (!window.confirm(`Delete rule "${ruleName}"? This cannot be undone.`)) return;
    try {
      await apiFetch(`/api/v1/rules/${ruleId}`, { method: 'DELETE' });
      onRefresh();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div>
      <div className="header-container">
        <h1 className="header-title">Rate Limiting Rules</h1>
        <p className="header-subtitle">Define request capacities, windows, and custom algorithm bindings.</p>
      </div>

      <button className="btn" onClick={() => setShowForm(!showForm)} style={{ marginBottom: '1rem' }}>
        {showForm ? 'Cancel' : '+ New Rule'}
      </button>

      {showForm && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 className="card-title">Create Rate Limit Rule</h3>
          <form onSubmit={handleCreate} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Rule Name</label>
              <input className="form-control" type="text" value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })} placeholder="e.g. API Rate Limit" required />
            </div>
            <div className="form-group">
              <label className="form-label">Identity Type</label>
              <select className="form-control" value={form.identity}
                onChange={e => setForm({ ...form, identity: e.target.value })}>
                <option value="ip">IP Address</option>
                <option value="api_key">API Key</option>
                <option value="user_id">User ID</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Algorithm</label>
              <AlgorithmSelector value={form.algorithm}
                onChange={v => setForm({ ...form, algorithm: v })} />
            </div>
            <div className="form-group">
              <label className="form-label">Endpoint (use * for all)</label>
              <input className="form-control" type="text" value={form.endpoint}
                onChange={e => setForm({ ...form, endpoint: e.target.value })} required />
            </div>
            <div className="form-group">
              <label className="form-label">Max Requests (Limit)</label>
              <input className="form-control" type="number" value={form.limit}
                onChange={e => setForm({ ...form, limit: parseInt(e.target.value) || 0 })} min="1" required />
            </div>
            <div className="form-group">
              <label className="form-label">Window (seconds)</label>
              <input className="form-control" type="number" value={form.window}
                onChange={e => setForm({ ...form, window: parseInt(e.target.value) || 0 })} min="1" required />
            </div>
            <button className="btn" type="submit" style={{ gridColumn: 'span 2' }}>Create Rule</button>
          </form>
        </div>
      )}

      <div className="grid-3">
        {(rules || []).length === 0 && (
          <p style={{ color: 'var(--text-secondary)', gridColumn: 'span 3' }}>No rules yet. Create one to start rate limiting.</p>
        )}
        {(rules || []).map(rule => (
          <div key={rule.id} style={{ position: 'relative' }}>
            <RuleCard rule={rule} />
            <button className="btn" style={{ width: '100%', marginTop: '0.5rem', background: 'var(--danger)' }}
              onClick={() => handleDelete(rule.id, rule.name)}>Delete</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RulesPage;
