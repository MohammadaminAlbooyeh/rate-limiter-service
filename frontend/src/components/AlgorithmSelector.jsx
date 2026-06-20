import React from 'react';

function AlgorithmSelector({ value, onChange }) {
  const algorithms = [
    'fixed_window',
    'sliding_window_log',
    'sliding_window_counter',
    'token_bucket',
    'leaky_bucket',
  ];

  return (
    <select value={value} onChange={e => onChange(e.target.value)}>
      {algorithms.map(algo => <option key={algo} value={algo}>{algo}</option>)}
    </select>
  );
}

export default AlgorithmSelector;
