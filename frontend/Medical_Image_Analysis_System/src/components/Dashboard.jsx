import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Dashboard({
  user,
  token,
  apiBaseUrl,
  onUserUpdated,
  onAccountDeleted
}) {
  const navigate = useNavigate();

  const [profileForm, setProfileForm] = useState({
    fullName: '',
    email: '',
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [deletePassword, setDeletePassword] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    setProfileForm((p) => ({
      ...p,
      fullName: user?.fullName || '',
      email: user?.email || ''
    }));
  }, [user]);

  const authHeaders = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (profileForm.newPassword) {
      if (profileForm.newPassword !== profileForm.confirmPassword) {
        setError('New password and confirm password do not match.');
        return;
      }
      if (profileForm.newPassword.length < 6) {
        setError('New password must be at least 6 characters.');
        return;
      }
      if (!profileForm.oldPassword) {
        setError('Current password is required to change password.');
        return;
      }
    }

    const payload = {
      fullName: profileForm.fullName,
      email: profileForm.email
    };

    if (profileForm.newPassword) {
      payload.oldPassword = profileForm.oldPassword;
      payload.newPassword = profileForm.newPassword;
    }

    try {
      setLoading(true);
      const { data } = await axios.put(
        `${apiBaseUrl}/api/auth/profile/update`,
        payload,
        { headers: authHeaders }
      );

      const updatedUser = { ...user, ...(data.user || {}) };
      onUserUpdated(updatedUser);
      setSuccess('Profile updated successfully.');
      setProfileForm((p) => ({
        ...p,
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }));
    } catch (err) {
      setError(err?.response?.data?.error || 'Profile update failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setError('');
    setSuccess('');

    if (!deletePassword) {
      setError('Password is required for account deletion.');
      return;
    }

    const confirmed = window.confirm(
      'This will permanently delete your account and data. Continue?'
    );
    if (!confirmed) return;

    try {
      setLoading(true);
      await axios.delete(`${apiBaseUrl}/api/auth/account/delete`, {
        headers: authHeaders,
        data: { password: deletePassword }
      });
      onAccountDeleted();
    } catch (err) {
      setError(err?.response?.data?.error || 'Account deletion failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-4 dashboard-page">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="mb-1">Dashboard</h2>
          <p className="text-muted mb-0">
            Welcome, <strong>{user?.fullName || user?.username}</strong>
          </p>
        </div>
      </div>

      {error && <div className="alert alert-danger py-2">{error}</div>}
      {success && <div className="alert alert-success py-2">{success}</div>}

      <div className="row g-4">
        <div className="col-lg-6">
          <div className="card shadow-sm h-100">
            <div className="card-header bg-primary text-white">
              <strong>Analysis Options</strong>
            </div>
            <div className="card-body">
              <p className="text-muted">
                Choose the analysis module you want to use.
              </p>

              <div className="d-grid gap-2">
                <button
                  className="btn btn-outline-danger"
                  onClick={() => navigate('/brain-tumor')}
                >
                  🧠 Brain Tumor Analysis
                </button>
                <button
                  className="btn btn-outline-info"
                  onClick={() => navigate('/covid-19')}
                >
                  🫁 Covid-19 Analysis
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card shadow-sm h-100">
            <div className="card-header bg-info text-white">
              <strong>Update Profile</strong>
            </div>
            <div className="card-body">
              <form onSubmit={handleUpdateProfile}>
                <div className="mb-3">
                  <label className="form-label">Full Name</label>
                  <input
                    className="form-control"
                    value={profileForm.fullName}
                    onChange={(e) =>
                      setProfileForm((p) => ({ ...p, fullName: e.target.value }))
                    }
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    value={profileForm.email}
                    onChange={(e) =>
                      setProfileForm((p) => ({ ...p, email: e.target.value }))
                    }
                  />
                </div>

                <hr />
                <h6>Change Password (optional)</h6>

                <div className="mb-2">
                  <label className="form-label">Current Password</label>
                  <input
                    type="password"
                    className="form-control"
                    value={profileForm.oldPassword}
                    onChange={(e) =>
                      setProfileForm((p) => ({ ...p, oldPassword: e.target.value }))
                    }
                  />
                </div>

                <div className="mb-2">
                  <label className="form-label">New Password</label>
                  <input
                    type="password"
                    className="form-control"
                    value={profileForm.newPassword}
                    onChange={(e) =>
                      setProfileForm((p) => ({ ...p, newPassword: e.target.value }))
                    }
                  />
                </div>

                <div className="mb-3">
                  <label className="form-label">Confirm New Password</label>
                  <input
                    type="password"
                    className="form-control"
                    value={profileForm.confirmPassword}
                    onChange={(e) =>
                      setProfileForm((p) => ({ ...p, confirmPassword: e.target.value }))
                    }
                  />
                </div>

                <button className="btn btn-info w-100" disabled={loading}>
                  {loading ? 'Updating...' : 'Update Profile'}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-12">
          <div className="card shadow-sm border-danger">
            <div className="card-header bg-danger text-white">
              <strong>Danger Zone</strong>
            </div>
            <div className="card-body">
              {!showDeleteConfirm ? (
                <button
                  className="btn btn-outline-danger"
                  onClick={() => setShowDeleteConfirm(true)}
                >
                  Delete Account
                </button>
              ) : (
                <div className="row g-2 align-items-end">
                  <div className="col-md-5">
                    <label className="form-label">Confirm Password</label>
                    <input
                      type="password"
                      className="form-control"
                      value={deletePassword}
                      onChange={(e) => setDeletePassword(e.target.value)}
                    />
                  </div>
                  <div className="col-md-7 d-flex gap-2">
                    <button
                      className="btn btn-danger"
                      onClick={handleDeleteAccount}
                      disabled={loading}
                    >
                      {loading ? 'Deleting...' : 'Confirm Delete'}
                    </button>
                    <button
                      className="btn btn-secondary"
                      onClick={() => {
                        setShowDeleteConfirm(false);
                        setDeletePassword('');
                      }}
                      disabled={loading}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}