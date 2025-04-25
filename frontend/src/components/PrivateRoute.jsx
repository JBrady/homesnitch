import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

export default function PrivateRoute({ children }) {
  const { authenticated, loading } = useContext(AuthContext);
  if (loading) return <div>Loading...</div>;
  return authenticated ? children : <Navigate to="/login" />;
}
