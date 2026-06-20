import React from 'react';

function ThresholdAlert({ alert }) {
  return (
    <div style={{ background: '#fff3cd', padding: 12, margin: 8, borderRadius: 4 }}>
      <strong>{alert.identity}</strong> has reached {alert.threshold} of rate limit
      ({alert.current}/{alert.limit})
    </div>
  );
}

export default ThresholdAlert;
