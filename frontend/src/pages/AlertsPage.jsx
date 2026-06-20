import React, { useState, useEffect } from 'react';
import ThresholdAlert from '../components/ThresholdAlert';

function AlertsPage() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    fetch('/api/v1/alerts')
      .then(res => res.json())
      .then(setAlerts);
  }, []);

  return (
    <div>
      <h1>Alerts</h1>
      {alerts.map((alert, i) => <ThresholdAlert key={i} alert={alert} />)}
    </div>
  );
}

export default AlertsPage;
