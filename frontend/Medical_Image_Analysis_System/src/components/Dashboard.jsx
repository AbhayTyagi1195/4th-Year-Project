import React from 'react';
import { useNavigate } from 'react-router-dom';

function Dashboard({ user, onLogout }) {
  const navigate = useNavigate();

  return (
    <div style={{ 
      padding: '50px', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
      minHeight: '100vh',
      color: 'white',
      fontFamily: 'Arial'
    }}>
      <h1>✅ DASHBOARD LOADED SUCCESSFULLY!</h1>
      
      <div style={{ background: 'rgba(255,255,255,0.2)', padding: '20px', borderRadius: '10px', marginTop: '20px' }}>
        <h2>User Information:</h2>
        <p><strong>Full Name:</strong> {user?.fullName || 'N/A'}</p>
        <p><strong>Username:</strong> {user?.username || 'N/A'}</p>
        <p><strong>Email:</strong> {user?.email || 'N/A'}</p>
      </div>
      
      <div style={{ marginTop: '30px' }}>
        <button 
          onClick={() => navigate('/brain-tumor')}
          style={{ 
            padding: '15px 30px', 
            marginRight: '15px', 
            fontSize: '16px', 
            cursor: 'pointer',
            background: '#4776e6',
            color: 'white',
            border: 'none',
            borderRadius: '8px'
          }}
        >
          🧠 Brain Tumor Analysis
        </button>
        
        <button 
          onClick={() => navigate('/covid-19')}
          style={{ 
            padding: '15px 30px', 
            marginRight: '15px', 
            fontSize: '16px', 
            cursor: 'pointer',
            background: '#f093fb',
            color: 'white',
            border: 'none',
            borderRadius: '8px'
          }}
        >
          🦠 COVID-19 Analysis
        </button>
        
        <button 
          onClick={onLogout}
          style={{ 
            padding: '15px 30px', 
            fontSize: '16px', 
            cursor: 'pointer',
            background: '#e53e3e',
            color: 'white',
            border: 'none',
            borderRadius: '8px'
          }}
        >
          🚪 Logout
        </button>
      </div>
    </div>
  );
}

export default Dashboard;