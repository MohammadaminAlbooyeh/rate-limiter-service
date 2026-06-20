import React, { useState, useEffect } from 'react';
import RequestChart from '../components/RequestChart';

function AnalyticsPage() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch('/api/v1/analytics/top?limit=20')
      .then(res => res.json())
      .then(setData);
  }, []);

  return (
    <div>
      <h1>Analytics</h1>
      <RequestChart />
      <table>
        <thead>
          <tr><th>Identity</th><th>Requests</th><th>Blocked</th></tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}><td>{row.identity}</td><td>{row.requests}</td><td>{row.blocked}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default AnalyticsPage;
