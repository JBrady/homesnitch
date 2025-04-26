import React, { createContext, useState, useEffect } from 'react';
import axios from 'axios';
import { refreshToken as apiRefresh } from '../utils/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiRefresh()
      .then(() => setAuthenticated(true))
      .catch(() => setAuthenticated(false))
      .finally(() => setLoading(false));
  }, []);

  const signIn = async (email, password) => {
    await axios.post('/auth/login', { email, password }, { withCredentials: true });
    setAuthenticated(true);
  };

  const signOut = async () => {
    await axios.post('/auth/logout', {}, { withCredentials: true });
    setAuthenticated(false);
  };

  const signUp = async (email, password) => {
    await axios.post('/auth/register', { email, password }, { withCredentials: true });
  };

  return (
    <AuthContext.Provider value={{ authenticated, loading, signIn, signOut, signUp }}>
      {children}
    </AuthContext.Provider>
  );
};
