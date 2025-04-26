import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Dashboard from '../pages/Dashboard';
import * as api from '../utils/api';
import { vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

vi.mock('../utils/api');

describe('Dashboard', () => {
  test('loads devices on mount and on rescan', async () => {
    // Mock API calls
    api.fetchScanResults.mockResolvedValue([
      { ip:'192.168.0.1', vendor:'TestCo', type:'Phone', query_count:5, data_sent:['example.com','test.org'], risk_level:'low' }
    ]);

    // Provide AuthContext and Router for Controls
    const wrapper = ({ children }) => (
      <AuthContext.Provider value={{ signOut: vi.fn() }}>
        <MemoryRouter>{children}</MemoryRouter>
      </AuthContext.Provider>
    );

    render(<Dashboard />, { wrapper });

    // initial load completes with success
    expect(await screen.findByText('Scan successful!')).toBeInTheDocument();
    expect(screen.getByText('192.168.0.1')).toBeInTheDocument();

    // click Rescan and expect the same flow
    userEvent.click(screen.getByText('Rescan'));
    // Rescan triggers a new fetch and ends with success
    expect(await screen.findByText('Scan successful!')).toBeInTheDocument();
  });
});
