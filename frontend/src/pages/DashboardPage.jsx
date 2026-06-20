import React, { useState, useEffect } from 'react';
import RequestChart from '../components/RequestChart';
import BlockedIPList from '../components/BlockedIPList';

function DashboardPage() {
  const [stats, setStats] = useState({ total: 0, allowed: 0, blocked: 0 });

  useEffect(() => {
    const interval = setInterval(async () => {
      const res = await fetch('/api/v1/analytics/usage?identity=all');
      const data = await res.json();
      setStats(data);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <div>
        <p>Total Requests: {stats.total_requests}</p>
        <p>Allowed: {stats.allowed_requests}</p>
        <p>Blocked: {stats.blocked_requests}</p>
      </div>
      <RequestChart />
      <BlockedIPList />
    </div>
  );
}

export default DashboardPage;
