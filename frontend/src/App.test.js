import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app title in sidebar', () => {
  render(<App />);
  const brand = screen.getByText(/RateLimiter.io/i);
  expect(brand).toBeInTheDocument();
});

test('renders navigation tabs', () => {
  render(<App />);
  expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
  expect(screen.getByText(/Rules/i)).toBeInTheDocument();
  expect(screen.getByText(/Analytics/i)).toBeInTheDocument();
  expect(screen.getByText(/Alerts/i)).toBeInTheDocument();
  expect(screen.getByText(/Settings/i)).toBeInTheDocument();
});
