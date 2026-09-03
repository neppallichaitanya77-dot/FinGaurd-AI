import { useState } from 'react';
import { User, Mail, Phone, Calendar, Shield, Loader2, Edit2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import { formatCurrency } from '../utils/helpers';

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    date_of_birth: user?.date_of_birth || '',
  });
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleSave = async () => {
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      const res = await authAPI.updateProfile(form);
      updateUser(res.data?.user || res.data);
      setSuccess('Profile updated successfully');
      setEditing(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const userInitial = (form.name || 'U').charAt(0).toUpperCase();

  return (
    <div className="flex-1 p-4 md:p-6 lg:p-8 max-w-3xl">
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-1">
          <User className="w-6 h-6 text-brand-600" />
          <h1 className="page-title">Profile</h1>
        </div>
        <p className="page-subtitle">Manage your account information</p>
      </div>

      <div className="card mb-6">
        <div className="flex items-center gap-4 mb-6">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-brand-500 to-fintech-teal flex items-center justify-center text-white text-3xl font-bold">
            {userInitial}
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900">{form.name || 'User'}</h2>
            <p className="text-gray-500 text-sm">{form.email}</p>
          </div>
          {!editing && (
            <button onClick={() => setEditing(true)} className="ml-auto btn-secondary text-sm py-2 flex items-center gap-1.5">
              <Edit2 className="w-4 h-4" /> Edit Profile
            </button>
          )}
        </div>

        {success && <div className="mb-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-sm text-emerald-600">{success}</div>}
        {error && <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-600">{error}</div>}

        <div className="space-y-4">
          <div>
            <label className="label-text">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="input-field pl-11"
                disabled={!editing}
              />
            </div>
          </div>

          <div>
            <label className="label-text">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="email"
                value={form.email}
                className="input-field pl-11 bg-gray-100"
                disabled
              />
            </div>
            <p className="text-xs text-gray-400 mt-1">Email cannot be changed</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="label-text">Phone Number</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="tel"
                  value={form.phone}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  placeholder="+91 XXXXX XXXXX"
                  className="input-field pl-11"
                  disabled={!editing}
                />
              </div>
            </div>
            <div>
              <label className="label-text">Date of Birth</label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="date"
                  value={form.date_of_birth}
                  onChange={(e) => setForm({ ...form, date_of_birth: e.target.value })}
                  className="input-field pl-11"
                  disabled={!editing}
                />
              </div>
            </div>
          </div>

          {editing && (
            <div className="flex gap-3 pt-2">
              <button onClick={handleSave} disabled={loading} className="btn-primary flex items-center gap-2">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save Changes'}
              </button>
              <button onClick={() => { setEditing(false); setForm({ name: user?.name || '', email: user?.email || '', phone: user?.phone || '', date_of_birth: user?.date_of_birth || '' }); }} className="btn-outline">
                Cancel
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5 text-brand-600" /> Account Information
        </h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-400">Member Since</p>
            <p className="font-medium text-gray-900">{user?.created_at ? new Date(user.created_at).toLocaleDateString('en-IN', { year: 'numeric', month: 'long' }) : 'September 2026'}</p>
          </div>
          <div>
            <p className="text-gray-400">Account Status</p>
            <p className="font-medium text-emerald-600">Active</p>
          </div>
          <div>
            <p className="text-gray-400">Account Type</p>
            <p className="font-medium text-gray-900">{user?.role || 'Customer'}</p>
          </div>
          <div>
            <p className="text-gray-400">Last Login</p>
            <p className="font-medium text-gray-900">{new Date().toLocaleDateString('en-IN')}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
