import React, { useState, useEffect } from 'react';
import RuleCard from '../components/RuleCard';

function RulesPage() {
  const [rules, setRules] = useState([]);

  useEffect(() => {
    fetch('/api/v1/rules')
      .then(res => res.json())
      .then(setRules);
  }, []);

  return (
    <div>
      <h1>Rate Limit Rules</h1>
      <button onClick={() => window.location = '/rules/new'}>New Rule</button>
      {rules.map(rule => <RuleCard key={rule.id} rule={rule} />)}
    </div>
  );
}

export default RulesPage;
