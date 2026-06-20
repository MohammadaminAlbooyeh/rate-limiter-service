import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

function RequestChart({ data = [] }) {
  return (
    <LineChart width={600} height={300} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="time" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="requests" stroke="#8884d8" />
      <Line type="monotone" dataKey="blocked" stroke="#ff7300" />
    </LineChart>
  );
}

export default RequestChart;
