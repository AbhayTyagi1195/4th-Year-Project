import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
  Link,
  useLocation,
  useNavigate
} from 'react-router-dom';

import 'bootstrap/dist/css/bootstrap.min.css';
import Dashboard from './components/Dashboard';
import BrainTumorAnalysis from './components/BrainTumorAnalysis';
import CovidAnalysis from './components/CovidAnalysis';

const API_BASE_URL = 'http://localhost:5000';

const getStoredAuth = () => {
  const token = localStorage.getItem('token');
  const userRaw = localStorage.getItem('user');
  let user = null;
  try {
    user = userRaw ? JSON.parse(userRaw) : null;
  } catch {
    user = null;
  }
  return { token, user };
};

function ProtectedRoute({ isAuthenticated, children }) {
  const location = useLocation();
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  return children;
}

function AuthPage({ mode, onLoginSuccess }) {
  const navigate = useNavigate();
  const isLogin = mode === 'login';

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [registerForm, setRegisterForm] = useState({
    fullName: '',
    username: '',
    email: '',
    password: ''
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const { data } = await axios.post(`${API_BASE_URL}/api/auth/login`, loginForm);
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
      onLoginSuccess(data.user, data.token);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err?.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/auth/register`, registerForm);
      navigate('/login', { replace: true });
    } catch (err) {
      setError(err?.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex align-items-center justify-content-center bg-light px-3">
      <div className="card shadow-sm" style={{ width: '100%', maxWidth: 460 }}>
        <div className="card-body p-4">
          <h3 className="text-center mb-1 text-nowrap">Medical Image Analysis System</h3>
          <p className="text-center text-muted mb-4">Brain Tumor & Covid-19 Detection</p>

          {error && <div className="alert alert-danger py-2">{error}</div>}

          {isLogin ? (
            <form onSubmit={handleLogin}>
              <div className="mb-3">
                <label className="form-label">Username</label>
                <input
                  className="form-control"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm((p) => ({ ...p, username: e.target.value }))}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-control"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm((p) => ({ ...p, password: e.target.value }))}
                  required
                />
              </div>
              <button className="btn btn-primary w-100" disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <div className="mb-3">
                <label className="form-label">Full Name</label>
                <input
                  className="form-control"
                  value={registerForm.fullName}
                  onChange={(e) => setRegisterForm((p) => ({ ...p, fullName: e.target.value }))}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Username</label>
                <input
                  className="form-control"
                  value={registerForm.username}
                  onChange={(e) => setRegisterForm((p) => ({ ...p, username: e.target.value }))}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Email</label>
                <input
                  type="email"
                  className="form-control"
                  value={registerForm.email}
                  onChange={(e) => setRegisterForm((p) => ({ ...p, email: e.target.value }))}
                  required
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Password</label>
                <input
                  type="password"
                  className="form-control"
                  value={registerForm.password}
                  onChange={(e) => setRegisterForm((p) => ({ ...p, password: e.target.value }))}
                  required
                  minLength={6}
                />
              </div>
              <button className="btn btn-success w-100" disabled={loading}>
                {loading ? 'Creating account...' : 'Register'}
              </button>
            </form>
          )}

          <div className="text-center mt-3">
            {isLogin ? (
              <Link to="/register">New user? Register</Link>
            ) : (
              <Link to="/login">Already have account? Login</Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function AppShell() {
  const navigate = useNavigate();
  const [{ token, user }, setAuth] = useState(getStoredAuth());

  const isAuthenticated = useMemo(() => Boolean(token && user), [token, user]);

  useEffect(() => {
    if (!isAuthenticated) return;
    axios.defaults.headers.common.Authorization = `Bearer ${token}`;
  }, [token, isAuthenticated]);

  const onLoginSuccess = (newUser, newToken) => {
    setAuth({ user: newUser, token: newToken });
  };

  const handleLogout = async () => {
    try {
      if (token) {
        await axios.post(`${API_BASE_URL}/api/auth/logout`, null, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch {
      // ignore logout api failure
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common.Authorization;
      setAuth({ token: null, user: null });
      navigate('/login', { replace: true });
    }
  };

  const handleUserUpdated = (updatedUser) => {
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setAuth((prev) => ({ ...prev, user: updatedUser }));
  };

  const handleAccountDeleted = () => {
    handleLogout();
  };

  return (
    <>
      {isAuthenticated && (
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
          <div className="container">
            <Link className="navbar-brand" to="/dashboard">Medical Image Analysis System</Link>
            <div className="navbar-nav me-auto">
              <Link className="nav-link" to="/dashboard">Dashboard</Link>
              <Link className="nav-link" to="/brain-tumor">Brain Tumor</Link>
              <Link className="nav-link" to="/covid-19">Covid-19</Link>
            </div>
            <div className="d-flex align-items-center gap-2">
              <span className="text-white-50 small">@{user?.username}</span>
              <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
                Logout
              </button>
            </div>
          </div>
        </nav>
      )}

      <Routes>
        <Route
          path="/"
          element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
        />
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <AuthPage mode="login" onLoginSuccess={onLoginSuccess} />
            )
          }
        />
        <Route
          path="/register"
          element={
            isAuthenticated ? (
              <Navigate to="/dashboard" replace />
            ) : (
              <AuthPage mode="register" onLoginSuccess={onLoginSuccess} />
            )
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <Dashboard
                user={user}
                token={token}
                apiBaseUrl={API_BASE_URL}
                onUserUpdated={handleUserUpdated}
                onAccountDeleted={handleAccountDeleted}
              />
            </ProtectedRoute>
          }
        />
        <Route
          path="/brain-tumor"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <BrainTumorAnalysis user={user} token={token} apiBaseUrl={API_BASE_URL} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/covid-19"
          element={
            <ProtectedRoute isAuthenticated={isAuthenticated}>
              <CovidAnalysis user={user} token={token} apiBaseUrl={API_BASE_URL} />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}