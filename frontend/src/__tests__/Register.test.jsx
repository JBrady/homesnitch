import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Register from '../pages/Register';
import { vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

describe('Register', () => {
  test('renders register form and submits successfully', async () => {
    const signUpMock = vi.fn().mockResolvedValue({});

    const wrapper = ({ children }) => (
      <AuthContext.Provider value={{ signUp: signUpMock }}>
        <MemoryRouter>{children}</MemoryRouter>
      </AuthContext.Provider>
    );

    render(<Register />, { wrapper });

    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();

    await userEvent.type(screen.getByPlaceholderText('Email'), 'new@example.com');
    await userEvent.type(screen.getByPlaceholderText('Password'), 'securepass');

    // Select the button specifically to avoid conflict with the heading
    await userEvent.click(screen.getByRole('button', { name: 'Register' }));

    await waitFor(() => {
      expect(signUpMock).toHaveBeenCalledWith('new@example.com', 'securepass');
    });
  });

  test('displays error on failed registration', async () => {
    const signUpMock = vi.fn().mockRejectedValue({
      response: { data: { msg: 'User already exists' } }
    });

    const wrapper = ({ children }) => (
      <AuthContext.Provider value={{ signUp: signUpMock }}>
        <MemoryRouter>{children}</MemoryRouter>
      </AuthContext.Provider>
    );

    render(<Register />, { wrapper });

    await userEvent.type(screen.getByPlaceholderText('Email'), 'exists@example.com');
    await userEvent.type(screen.getByPlaceholderText('Password'), 'password');

    // Select the button specifically to avoid conflict with the heading
    await userEvent.click(screen.getByRole('button', { name: 'Register' }));

    expect(await screen.findByText('User already exists')).toBeInTheDocument();
  });
});
