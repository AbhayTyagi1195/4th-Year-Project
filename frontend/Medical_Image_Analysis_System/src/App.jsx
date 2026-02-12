import { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [authMode, setAuthMode] = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    username: '', email: '', password: '', fullName: ''
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      try {
        setUser(JSON.parse(userData));
        setIsAuthenticated(true);
      } catch (err) {
        localStorage.clear();
      }
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        setUser(data.user);
        setIsAuthenticated(true);
        setCurrentPage('dashboard');
      } else {
        setError(data.error || 'Login failed');
      }
    } catch (err) {
      setError('Connection error. Please check if backend is running on port 5000.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerForm)
      });

      const data = await response.json();

      if (response.ok) {
        alert('✅ Registration successful! Please login.');
        setAuthMode('login');
        setRegisterForm({ username: '', email: '', password: '', fullName: '' });
      } else {
        setError(data.error || 'Registration failed');
      }
    } catch (err) {
      setError('Connection error. Please check if backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    setIsAuthenticated(false);
    setCurrentPage('dashboard');
  };

  const navigate = (page) => {
    setCurrentPage(page);
  };

  // LOGIN SCREEN
  if (!isAuthenticated) {
    return (
      <div className="auth-gradient-bg">
        <div className="auth-card">
          <div className="auth-card-header">
            <div className="brain-icon">🏥</div>
            <h2>Medical Image Analysis System</h2>
            <p>AI-Powered Multi-Disease Detection Platform</p>
          </div>

          <div className="auth-card-body">
            <div className="auth-tabs">
              <button
                className={`auth-tab-btn ${authMode === 'login' ? 'active' : ''}`}
                onClick={() => setAuthMode('login')}
              >
                Login
              </button>
              <button
                className={`auth-tab-btn ${authMode === 'register' ? 'active' : ''}`}
                onClick={() => setAuthMode('register')}
              >
                Register
              </button>
            </div>

            {error && <div className="alert-error">⚠️ {error}</div>}

            {authMode === 'login' ? (
              <form onSubmit={handleLogin}>
                <div className="form-group">
                  <label className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-input"
                    value={loginForm.username}
                    onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
                    placeholder="Enter your username"
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    className="form-input"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                    placeholder="Enter your password"
                    required
                  />
                </div>
                <button type="submit" className="btn-submit" disabled={loading}>
                  {loading ? 'Logging In...' : 'Login'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister}>
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    className="form-input"
                    value={registerForm.fullName}
                    onChange={(e) => setRegisterForm({...registerForm, fullName: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Username</label>
                  <input
                    type="text"
                    className="form-input"
                    value={registerForm.username}
                    onChange={(e) => setRegisterForm({...registerForm, username: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-input"
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm({...registerForm, email: e.target.value})}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input
                    type="password"
                    className="form-input"
                    value={registerForm.password}
                    onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
                    required
                    minLength="6"
                  />
                </div>
                <button type="submit" className="btn-submit" disabled={loading}>
                  {loading ? 'Creating Account...' : 'Register'}
                </button>
              </form>
            )}
          </div>

          <div className="auth-card-footer">
            <small>🔒 Your data is secure and encrypted</small>
          </div>
        </div>
      </div>
    );
  }

  // DASHBOARD PAGES (NO ROUTER!)
  return (
    <div>
      {currentPage === 'dashboard' && (
        <Dashboard user={user} onLogout={handleLogout} navigate={navigate} />
      )}
      {currentPage === 'brain-tumor' && (
        <BrainTumorAnalysis user={user} onLogout={handleLogout} navigate={navigate} />
      )}
      {currentPage === 'covid-19' && (
        <CovidAnalysis user={user} onLogout={handleLogout} navigate={navigate} />
      )}
    </div>
  );
}

// ========== DASHBOARD COMPONENT (NO HOOKS!) ==========
function Dashboard({ user, onLogout, navigate }) {
  return (
    <div style={{ 
      padding: '50px', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
      minHeight: '100vh',
      color: 'white'
    }}>
      <h1>✅ DASHBOARD WORKING!</h1>
      
      <div style={{ background: 'rgba(255,255,255,0.2)', padding: '20px', borderRadius: '10px', marginTop: '20px' }}>
        <h2>User Information:</h2>
        <p><strong>Full Name:</strong> {user?.fullName}</p>
        <p><strong>Username:</strong> {user?.username}</p>
        <p><strong>Email:</strong> {user?.email}</p>
      </div>
      
      <div style={{ marginTop: '30px' }}>
        <button 
          onClick={() => navigate('brain-tumor')}
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
          onClick={() => navigate('covid-19')}
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

// ========== BRAIN TUMOR COMPONENT (NO HOOKS!) ==========
function BrainTumorAnalysis({ user, onLogout, navigate }) {
  return (
    <div style={{ padding: '50px', background: '#e0f7ff', minHeight: '100vh' }}>
      <h1>🧠 Brain Tumor Analysis</h1>
      <p><strong>User:</strong> {user?.fullName}</p>
      
      <button 
        onClick={() => navigate('dashboard')}
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

// ========== COVID COMPONENT (NO HOOKS!) ==========
function CovidAnalysis({ user, onLogout, navigate }) {
  return (
    <div style={{ padding: '50px', background: '#ffe0e0', minHeight: '100vh' }}>
      <h1>🦠 COVID-19 Analysis</h1>
      <p><strong>User:</strong> {user?.fullName}</p>
      
      <button 
        onClick={() => navigate('dashboard')}
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

export default App;