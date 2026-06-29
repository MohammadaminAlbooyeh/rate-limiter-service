import React, { useState, useEffect, useCallback } from 'react';
import DashboardPage from './pages/DashboardPage';
import RulesPage from './pages/RulesPage';
import AnalyticsPage from './pages/AnalyticsPage';
import AlertsPage from './pages/AlertsPage';
import SettingsPage from './pages/SettingsPage';

const apiHost = process.env.REACT_APP_API_URL || '';
const ADMIN_KEY_STORAGE = 'rate_limiter_admin_key';

function getAdminKey() {
  return localStorage.getItem(ADMIN_KEY_STORAGE) || '';
}

function apiFetch(path, options = {}) {
  const adminKey = getAdminKey();
  const headers = { ...(options.headers || {}) };
  if (adminKey) headers['X-Admin-Key'] = adminKey;
  if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
  return fetch(`${apiHost}${path}`, { ...options, headers });
}

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [stats, setStats] = useState({ total_requests: 0, allowed_requests: 0, blocked_requests: 0 });
  const [rules, setRules] = useState([]);
  const [blockedLogs, setBlockedLogs] = useState([]);
  const [topConsumers, setTopConsumers] = useState([]);
  const [timeline, setTimeline] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [whitelist, setWhitelist] = useState([]);
  const [blacklist, setBlacklist] = useState([]);
  const [adminKeyInput, setAdminKeyInput] = useState(getAdminKey());
  const [simResult, setSimResult] = useState(null);
  const simFormDefaults = { ip: '192.168.1.1', api_key: '', user_id: '', endpoint: '/home', method: 'GET' };
  const [simForm, setSimForm] = useState(simFormDefaults);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, blockedRes, rulesRes, topRes, timelineRes, alertsRes, whitelistRes, blacklistRes] = await Promise.all([
        apiFetch('/api/v1/analytics/usage?identity=all'),
        apiFetch('/api/v1/analytics/blocked'),
        apiFetch('/api/v1/rules'),
        apiFetch('/api/v1/analytics/top?limit=10'),
        apiFetch('/api/v1/analytics/timeline?minutes=30'),
        apiFetch('/api/v1/alerts'),
        apiFetch('/api/v1/whitelist'),
        apiFetch('/api/v1/blacklist'),
      ]);
      if (statsRes.ok) setStats(await statsRes.json());
      if (blockedRes.ok) setBlockedLogs(await blockedRes.json());
      if (rulesRes.ok) setRules(await rulesRes.json());
      if (topRes.ok) setTopConsumers(await topRes.json());
      if (timelineRes.ok) setTimeline(await timelineRes.json());
      if (alertsRes.ok) setAlerts(await alertsRes.json());
      if (whitelistRes.ok) setWhitelist(await whitelistRes.json());
      if (blacklistRes.ok) setBlacklist(await blacklistRes.json());
    } catch (e) {
      console.error('Failed to fetch dashboard data', e);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = window.location.hostname;
    const wsPort = window.location.port === '3000' ? '8000' : window.location.port;
    const wsUrl = `${wsProto}//${wsHost}${wsPort ? `:${wsPort}` : ''}/ws/analytics`;
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'log') {
          const log = msg.data;
          setStats(prev => ({
            total_requests: (prev.total_requests || 0) + 1,
            allowed_requests: (prev.allowed_requests || 0) + (log.allowed ? 1 : 0),
            blocked_requests: (prev.blocked_requests || 0) + (log.allowed ? 0 : 1),
          }));
          if (!log.allowed) setBlockedLogs(prev => [log, ...prev.slice(0, 49)]);
          setTopConsumers(prev => {
            const exists = prev.find(c => c.identity === log.identity);
            if (exists) {
              return prev.map(c => c.identity === log.identity
                ? { ...c, total_requests: c.total_requests + 1 } : c)
                .sort((a, b) => b.total_requests - a.total_requests);
            }
            return [...prev, { identity: log.identity, total_requests: 1 }]
              .sort((a, b) => b.total_requests - a.total_requests).slice(0, 10);
          });
        }
      } catch (e) { /* ignore parse errors */ }
    };
    const interval = setInterval(fetchData, 10000);
    return () => { ws.close(); clearInterval(interval); };
  }, [fetchData]);

  const handleSimulateRequest = async (e) => {
    e.preventDefault();
    try {
      const res = await apiFetch('/api/v1/check', {
        method: 'POST',
        body: JSON.stringify(simForm),
      });
      const data = await res.json();
      setSimResult({
        status: res.status,
        allowed: res.status !== 429 && res.status !== 403,
        detail: data.detail || 'Success',
        limit: res.headers.get('X-RateLimit-Limit'),
        remaining: res.headers.get('X-RateLimit-Remaining'),
        reset: res.headers.get('X-RateLimit-Reset'),
        algorithm: res.headers.get('X-RateLimit-Algorithm'),
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveAdminKey = () => {
    localStorage.setItem(ADMIN_KEY_STORAGE, adminKeyInput);
  };

  const handleAddListEntry = async (form) => {
    const endpoint = form.type === 'whitelist' ? '/api/v1/whitelist' : '/api/v1/blacklist';
    await apiFetch(endpoint, {
      method: 'POST',
      body: JSON.stringify({ identity: form.identity, reason: form.reason }),
    });
    fetchData();
  };

  const handleDeleteListEntry = async (type, identity) => {
    await apiFetch(`/api/v1/${type}/${encodeURIComponent(identity)}`, { method: 'DELETE' });
    fetchData();
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="sidebar-brand">RateLimiter.io</div>
        <ul className="nav-links">
          {[
            { key: 'dashboard', label: 'Dashboard' },
            { key: 'rules', label: 'Rules' },
            { key: 'analytics', label: 'Analytics' },
            { key: 'alerts', label: 'Alerts' },
            { key: 'lists', label: 'Whitelist / Blacklist' },
            { key: 'settings', label: 'Settings' },
          ].map(item => (
            <li key={item.key}
              className={`nav-item ${activeTab === item.key ? 'active' : ''}`}
              onClick={() => setActiveTab(item.key)}>
              {item.label}
            </li>
          ))}
        </ul>
      </div>

      <div className="main-content">
        {activeTab === 'dashboard' && (
          <DashboardPage
            stats={stats}
            blockedLogs={blockedLogs}
            topConsumers={topConsumers}
            timeline={timeline}
            simForm={simForm}
            simResult={simResult}
            onSimFormChange={setSimForm}
            onSimulate={handleSimulateRequest}
            onRefresh={fetchData}
          />
        )}

        {activeTab === 'rules' && (
          <RulesPage rules={rules} onRefresh={fetchData} apiFetch={apiFetch} />
        )}

        {activeTab === 'analytics' && (
          <AnalyticsPage data={topConsumers} timeline={timeline} blockedLogs={blockedLogs} />
        )}

        {activeTab === 'alerts' && (
          <AlertsPage alerts={alerts} onRefresh={fetchData} />
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
                <form onSubmit={(e) => { e.preventDefault(); const fd = new FormData(e.target); handleAddListEntry({ identity: fd.get('identity'), reason: fd.get('reason'), type: fd.get('type') }); }}>
                  <div className="form-group">
                    <label className="form-label">Client Identity (IP/User ID/API Key)</label>
                    <input className="form-control" type="text" name="identity" placeholder="e.g. 192.168.1.1" required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Reason / Notes</label>
                    <input className="form-control" type="text" name="reason" placeholder="e.g. VIP User Bypass" />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Type</label>
                    <select className="form-control" name="type">
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
                      <div><p className="list-item-title">{w.identity}</p><p className="list-item-subtitle">{w.reason}</p></div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className="badge success">Whitelisted</span>
                        <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', background: 'var(--danger)' }}
                          onClick={() => handleDeleteListEntry('whitelist', w.identity)}>Remove</button>
                      </div>
                    </div>
                  ))}
                  {whitelist.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No whitelisted clients.</p>}
                </div>
                <h4>Always Denied (Blacklist)</h4>
                <div className="list-container">
                  {blacklist.map((b, i) => (
                    <div className="list-item" key={i}>
                      <div><p className="list-item-title">{b.identity}</p><p className="list-item-subtitle">{b.reason}</p></div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className="badge danger">Blacklisted</span>
                        <button className="btn" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem', background: 'var(--danger)' }}
                          onClick={() => handleDeleteListEntry('blacklist', b.identity)}>Remove</button>
                      </div>
                    </div>
                  ))}
                  {blacklist.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No blacklisted clients.</p>}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <SettingsPage
            adminKey={adminKeyInput}
            onAdminKeyChange={setAdminKeyInput}
            onSaveAdminKey={handleSaveAdminKey}
          />
        )}
      </div>
    </div>
  );
}

export default App;
