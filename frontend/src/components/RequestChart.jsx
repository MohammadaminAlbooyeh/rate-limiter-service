import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function RequestChart({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, #e0e0e0)" />
        <XAxis dataKey="time" stroke="var(--text-secondary, #888)" fontSize={12} />
        <YAxis stroke="var(--text-secondary, #888)" fontSize={12} />
        <Tooltip
          contentStyle={{
            background: 'var(--card-bg, #fff)',
            border: '1px solid var(--border-color, #ddd)',
            borderRadius: '6px',
          }}
        />
        <Legend />
        <Line type="monotone" dataKey="total" name="Total Requests" stroke="#3b82f6" strokeWidth={2} dot={false} />
        <Line type="monotone" dataKey="blocked" name="Blocked" stroke="#ef4444" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default RequestChart;
