import React, { useState, useEffect } from 'react';

function BlockedIPList() {
  const [blocked, setBlocked] = useState([]);

  useEffect(() => {
    fetch('/api/v1/analytics/blocked')
      .then(res => res.json())
      .then(setBlocked);
  }, []);

  return (
    <div>
      <h2>Blocked IPs</h2>
      <ul>
        {blocked.map((entry, i) => <li key={i}>{entry.ip}</li>)}
      </ul>
    </div>
  );
}

export default BlockedIPList;
