import React from 'react';
import { useNavigate } from 'react-router-dom';

function BrainTumorAnalysis({ user, onLogout }) {
  const navigate = useNavigate();

  return (
    <div style={{ padding: '50px', background: '#e0f7ff', minHeight: '100vh' }}>
      <h1>🧠 Brain Tumor Analysis Page</h1>
      <p><strong>User:</strong> {user?.fullName}</p>
      
      <button 
        onClick={() => navigate('/dashboard')}
        style={{ padding: '10px 20px', marginRight: '10px', cursor: 'pointer' }}
      >
        ← Back to Dashboard
      </button>
      
      <button 
        onClick={onLogout}
        style={{ padding: '10px 20px', cursor: 'pointer', background: '#e53e3e', color: 'white', border: 'none' }}
      >
        Logout
      </button>
    </div>
  );
}

export default BrainTumorAnalysis;