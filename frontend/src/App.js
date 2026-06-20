import React, { useState, useEffect } from 'react';
import RequestChart from './components/RequestChart';
import AlgorithmSelector from './components/AlgorithmSelector';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({ total_requests: 0, allowed_requests: 0, blocked_requests: 0 });
  const [rules, setRules] = useState([]);
  const [blockedLogs, setBlockedLogs] = useState([]);
  const [topConsumers, setTopConsumers] = useState([]);
  
  // Whitelist/Blacklist lists
  const [whitelist, setWhitelist] = useState([]);
  const [blacklist, setBlacklist] = useState([]);
  
  // Forms
  const [ruleForm, setRuleForm] = useState({ name: '', algorithm: 'fixed_window', limit: 100, window: 60, endpoint: '*', identity: 'ip' });
  const [listForm, setListForm] = useState({ identity: '', reason: '', type: 'whitelist' });
  const [simForm, setSimForm] = useState({ identity: 'test_user', endpoint: '/home', method: 'GET' });
  const [simResult, setSimResult] = useState(null);

  // Poll usage statistics and logs
  const fetchData = async () => {
    try {
      const statsRes = await fetch('/api/v1/analytics/usage?identity=all');
      const statsData = await statsRes.json();
      setStats(statsData);

      const blockedRes = await fetch('/api/v1/analytics/blocked');
      const blockedData = await blockedRes.json();
      setBlockedLogs(blockedData);

      const rulesRes = await fetch('/api/v1/rules');
      const rulesData = await rulesRes.json();
      setRules(rulesData);

      const topRes = await fetch('/api/v1/analytics/top?limit=10');
      const topData = await topRes.json();
      setTopConsumers(topData);
    } catch (e) {
      console.error("Failed to fetch dashboard data", e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateRule = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/v1/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ruleForm)
      });
      if (res.ok) {
        setRuleForm({ name: '', algorithm: 'fixed_window', limit: 100, window: 60, endpoint: '*', identity: 'ip' });
        fetchData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteRule = async (ruleId) => {
    try {
      await fetch(`/api/v1/rules/${ruleId}`, { method: 'DELETE' });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddList = async (e) => {
    e.preventDefault();
    try {
      const endpoint = listForm.type === 'whitelist' ? '/api/v1/whitelist' : '/api/v1/blacklist';
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identity: listForm.identity, reason: listForm.reason })
      });
      if (res.ok) {
        if (listForm.type === 'whitelist') {
          setWhitelist([...whitelist, { identity: listForm.identity, reason: listForm.reason }]);
        } else {
          setBlacklist([...blacklist, { identity: listForm.identity, reason: listForm.reason }]);
        }
        setListForm({ identity: '', reason: '', type: 'whitelist' });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSimulateRequest = async (e) => {
    e.preventDefault();
    try {
      // Build identity payload for endpoint check
      const payload = {
        endpoint: simForm.endpoint,
        method: simForm.method,
        ip: simForm.identity,
        api_key: simForm.identity,
        user_id: simForm.identity
      };
      
      const res = await fetch('/api/v1/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const status = res.status;
      const data = await res.json();
      
      setSimResult({
        status,
        allowed: status !== 429 && status !== 403,
        detail: data.detail || 'Success',
        remaining: res.headers.get('X-RateLimit-Remaining'),
        reset: res.headers.get('Retry-After')
      });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="sidebar-brand">
          🛡️ RateLimiter.io
        </div>
        <ul className="nav-links">
          <li className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
            📊 Dashboard
          </li>
          <li className={`nav-item ${activeTab === 'rules' ? 'active' : ''}`} onClick={() => setActiveTab('rules')}>
            ⚙️ Limits & Rules
          </li>
          <li className={`nav-item ${activeTab === 'lists' ? 'active' : ''}`} onClick={() => setActiveTab('lists')}>
            🚫 Whitelist / Blacklist
          </li>
        </ul>
      </div>

      <div className="main-content">
        {activeTab === 'dashboard' && (
          <div>
            <div className="header-container">
              <h1 className="header-title">Analytics Dashboard</h1>
              <p className="header-subtitle">Real-time stats, rate limiting decisions, and system performance logs.</p>
            </div>

            <div className="grid-3">
              <div className="stat-card">
                <div className="stat-label">Total Requests</div>
                <div className="stat-value total">{stats.total_requests || 0}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Allowed Requests</div>
                <div className="stat-value allowed">{stats.allowed_requests || 0}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Blocked Requests</div>
                <div className="stat-value blocked">{stats.blocked_requests || 0}</div>
              </div>
            </div>

            <div className="grid-3" style={{ gridTemplateColumns: '2fr 1fr' }}>
              <div className="card">
                <h3 className="card-title">Live Simulator Tool</h3>
                <form onSubmit={handleSimulateRequest} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: '1rem', alignItems: 'end' }}>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label">Client Identity Value (IP/API Key/User ID)</label>
                    <input className="form-control" type="text" value={simForm.identity} onChange={e => setSimForm({ ...simForm, identity: e.target.value })} required />
                  </div>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label">Endpoint</label>
                    <input className="form-control" type="text" value={simForm.endpoint} onChange={e => setSimForm({ ...simForm, endpoint: e.target.value })} required />
                  </div>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label">HTTP Method</label>
                    <select className="form-control" value={simForm.method} onChange={e => setSimForm({ ...simForm, method: e.target.value })}>
                      <option value="GET">GET</option>
                      <option value="POST">POST</option>
                      <option value="DELETE">DELETE</option>
                    </select>
                  </div>
                  <button className="btn" type="submit">Send Test Request</button>
                </form>

                {simResult && (
                  <div style={{ marginTop: '1.5rem', padding: '1rem', borderRadius: '8px', background: simResult.allowed ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${simResult.allowed ? 'var(--success)' : 'var(--danger)'}` }}>
                    <strong>Response Status:</strong> {simResult.status} <br/>
                    <strong>Allowed:</strong> {simResult.allowed ? 'YES' : 'NO'} <br/>
                    <strong>Details:</strong> {simResult.detail} <br/>
                    {simResult.remaining && <><strong>Remaining Slots:</strong> {simResult.remaining} <br/></>}
                    {simResult.reset && <><strong>Retry After:</strong> {simResult.reset}s <br/></>}
                  </div>
                )}
              </div>

              <div className="card">
                <h3 className="card-title">Top Consumers</h3>
                <div className="list-container">
                  {topConsumers.map((consumer, index) => (
                    <div className="list-item" key={index} style={{ padding: '0.5rem 1rem' }}>
                      <span>{consumer.identity}</span>
                      <span className="badge success">{consumer.total_requests} reqs</span>
                    </div>
                  ))}
                  {topConsumers.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No request data available.</p>}
                </div>
              </div>
            </div>

            <div className="card">
              <h3 className="card-title">Recently Blocked Requests</h3>
              <div className="list-container">
                {blockedLogs.map((log, index) => (
                  <div className="list-item" key={index}>
                    <div>
                      <p className="list-item-title">{log.identity}</p>
                      <p className="list-item-subtitle">{log.method} {log.endpoint} • {new Date(log.timestamp).toLocaleTimeString()}</p>
                    </div>
                    <span className="badge danger">Blocked</span>
                  </div>
                ))}
                {blockedLogs.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No recently blocked requests.</p>}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'rules' && (
          <div>
            <div className="header-container">
              <h1 className="header-title">Rate Limiting Rules</h1>
              <p className="header-subtitle">Define request capacities, windows, and custom algorithm bindings.</p>
            </div>

            <div className="grid-3" style={{ gridTemplateColumns: '1fr 2fr' }}>
              <div className="card">
                <h3 className="card-title">Create New Rule</h3>
                <form onSubmit={handleCreateRule}>
                  <div className="form-group">
                    <label className="form-label">Rule Name</label>
                    <input className="form-control" type="text" value={ruleForm.name} onChange={e => setRuleForm({ ...ruleForm, name: e.target.value })} placeholder="e.g. Premium Tier Limit" required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Algorithm</label>
                    <div className="form-control" style={{ padding: 0 }}>
                      <AlgorithmSelector value={ruleForm.algorithm} onChange={val => setRuleForm({ ...ruleForm, algorithm: val })} />
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Rate Limit Capacity</label>
                    <input className="form-control" type="number" value={ruleForm.limit} onChange={e => setRuleForm({ ...ruleForm, limit: parseInt(e.target.value) })} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Time Window (seconds)</label>
                    <input className="form-control" type="number" value={ruleForm.window} onChange={e => setRuleForm({ ...ruleForm, window: parseInt(e.target.value) })} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Identity Match Attribute</label>
                    <select className="form-control" value={ruleForm.identity} onChange={e => setRuleForm({ ...ruleForm, identity: e.target.value })}>
                      <option value="ip">Client IP Address</option>
                      <option value="api_key">API Key (Header)</option>
                      <option value="user_id">User ID (Header)</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Endpoint Path Pattern</label>
                    <input className="form-control" type="text" value={ruleForm.endpoint} onChange={e => setRuleForm({ ...ruleForm, endpoint: e.target.value })} required />
                  </div>
                  <button className="btn" type="submit" style={{ width: '100%' }}>Create Rule</button>
                </form>
              </div>

              <div className="card">
                <h3 className="card-title">Active Rules</h3>
                <div className="list-container">
                  {rules.map(rule => (
                    <div className="list-item" key={rule.id}>
                      <div>
                        <p className="list-item-title">{rule.name}</p>
                        <p className="list-item-subtitle">
                          Allows {rule.limit} requests / {rule.window}s matching endpoint <code>{rule.endpoint}</code> using <code>{rule.identity}</code> key.
                        </p>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                        <span className="badge algorithm">{rule.algorithm}</span>
                        <button className="btn btn-secondary btn-danger" onClick={() => handleDeleteRule(rule.id)} style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}>Delete</button>
                      </div>
                    </div>
                  ))}
                  {rules.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No active rules defined yet.</p>}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'lists' && (
          <div>
            <div className="header-container">
              <h1 className="header-title">Whitelist & Blacklist</h1>
              <p className="header-subtitle">Directly allow or deny specific clients before algorithm execution.</p>
            </div>

            <div className="grid-3" style={{ gridTemplateColumns: '1fr 2fr' }}>
              <div className="card">
                <h3 className="card-title">Add Identity Entry</h3>
                <form onSubmit={handleAddList}>
                  <div className="form-group">
                    <label className="form-label">Client Identity (IP/User ID/API Key)</label>
                    <input className="form-control" type="text" value={listForm.identity} onChange={e => setListForm({ ...listForm, identity: e.target.value })} placeholder="e.g. 192.168.1.1" required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Reason / Notes</label>
                    <input className="form-control" type="text" value={listForm.reason} onChange={e => setListForm({ ...listForm, reason: e.target.value })} placeholder="e.g. VIP User Bypass" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Type</label>
                    <select className="form-control" value={listForm.type} onChange={e => setListForm({ ...listForm, type: e.target.value })}>
                      <option value="whitelist">Whitelist (Always Allow)</option>
                      <option value="blacklist">Blacklist (Always Block)</option>
                    </select>
                  </div>
                  <button className="btn" type="submit" style={{ width: '100%' }}>Add Entry</button>
                </form>
              </div>

              <div className="card">
                <h3 className="card-title">Whitelisted & Blacklisted Client Registries</h3>
                <h4>Always Allowed (Whitelist)</h4>
                <div className="list-container" style={{ marginBottom: '2rem' }}>
                  {whitelist.map((w, i) => (
                    <div className="list-item" key={i}>
                      <div>
                        <p className="list-item-title">{w.identity}</p>
                        <p className="list-item-subtitle">{w.reason}</p>
                      </div>
                      <span className="badge success">Whitelisted</span>
                    </div>
                  ))}
                  {whitelist.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No whitelisted clients.</p>}
                </div>

                <h4>Always Denied (Blacklist)</h4>
                <div className="list-container">
                  {blacklist.map((b, i) => (
                    <div className="list-item" key={i}>
                      <div>
                        <p className="list-item-title">{b.identity}</p>
                        <p className="list-item-subtitle">{b.reason}</p>
                      </div>
                      <span className="badge danger">Blacklisted</span>
                    </div>
                  ))}
                  {blacklist.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No blacklisted clients.</p>}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
