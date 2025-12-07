import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Login from '../pages/Login';
import { vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

describe('Login', () => {
  test('renders login form and submits successfully', async () => {
    const signInMock = vi.fn().mockResolvedValue({});

    const wrapper = ({ children }) => (
      <AuthContext.Provider value={{ signIn: signInMock }}>
        <MemoryRouter>{children}</MemoryRouter>
      </AuthContext.Provider>
    );

    render(<Login />, { wrapper });

    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();

    await userEvent.type(screen.getByPlaceholderText('Email'), 'test@example.com');
    await userEvent.type(screen.getByPlaceholderText('Password'), 'password123');

    // Select the button specifically to avoid conflict with the heading
    await userEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    await waitFor(() => {
      expect(signInMock).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });

  test('displays error on failed login', async () => {
    const signInMock = vi.fn().mockRejectedValue({
      response: { data: { msg: 'Invalid credentials' } }
    });

    const wrapper = ({ children }) => (
      <AuthContext.Provider value={{ signIn: signInMock }}>
        <MemoryRouter>{children}</MemoryRouter>
      </AuthContext.Provider>
    );

    render(<Login />, { wrapper });

    await userEvent.type(screen.getByPlaceholderText('Email'), 'wrong@example.com');
    await userEvent.type(screen.getByPlaceholderText('Password'), 'wrongpass');

    // Select the button specifically to avoid conflict with the heading
    await userEvent.click(screen.getByRole('button', { name: 'Sign In' }));

    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument();
  });
});
