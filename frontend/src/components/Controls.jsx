import React, { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

export default function Controls({ onRescan, onTest }) {
  const { signOut } = useContext(AuthContext);
  const navigate = useNavigate();
  return (
    <div className="flex space-x-2 mb-4">
      <button
        className="px-4 py-2 bg-blue-600 text-white rounded"
        onClick={onRescan}
      >
        Rescan
      </button>
      <button
        className="px-4 py-2 bg-green-600 text-white rounded"
        onClick={onTest}
      >
        Test Agent
      </button>
      <button
        className="px-4 py-2 bg-red-600 text-white rounded"
        onClick={() => { signOut(); navigate('/login'); }}
      >
        Logout
      </button>
    </div>
  );
}