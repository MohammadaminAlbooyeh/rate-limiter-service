import React from 'react';

function RuleCard({ rule }) {
  return (
    <div style={{ border: '1px solid #ccc', padding: 16, margin: 8 }}>
      <h3>{rule.name}</h3>
      <p>Algorithm: {rule.algorithm}</p>
      <p>Limit: {rule.limit} / {rule.window}s</p>
      <p>Identity: {rule.identity}</p>
      <p>Endpoint: {rule.endpoint}</p>
    </div>
  );
}

export default RuleCard;
