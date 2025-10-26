import React, { useState, useEffect } from 'react';
import { Save, Lock, Folder, Clock, Upload } from 'lucide-react';
import { settingsApi, SettingsData } from '../services/settingsApi';
import { SettingsLoading } from '../components/LoadingSpinner';

const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  
  // Password change state
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      const data = await settingsApi.getSettings();
      setSettings(data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load settings' });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSettings = async () => {
    if (!settings) return;
    
    setSaving(true);
    setMessage(null);
    
    try {
      await settingsApi.updateSettings(settings);
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save settings' });
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (newPassword !== confirmPassword) {
      setMessage({ type: 'error', text: 'Passwords do not match' });
      return;
    }
    
    if (newPassword.length < 6) {
      setMessage({ type: 'error', text: 'Password must be at least 6 characters' });
      return;
    }
    
    setSaving(true);
    setMessage(null);
    
    try {
      await settingsApi.changePassword(currentPassword, newPassword);
      setMessage({ type: 'success', text: 'Password changed successfully!' });
      setShowPasswordForm(false);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <SettingsLoading fullScreen />;
  }

  if (!settings) {
    return <div className="p-6 text-red-500">Failed to load settings</div>;
  }

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-2xl font-bold text-white mb-6">Settings</h1>
      
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-900/50 text-green-200' : 'bg-red-900/50 text-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Account Section */}
      <section className="mb-8 bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Lock size={20} />
          Account
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Username</label>
            <input
              type="text"
              value={settings.user.username}
              disabled
              className="w-full px-4 py-2 bg-gray-700 text-gray-400 rounded-lg cursor-not-allowed"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-1">Email</label>
            <input
              type="email"
              value={settings.user.email}
              disabled
              className="w-full px-4 py-2 bg-gray-700 text-gray-400 rounded-lg cursor-not-allowed"
            />
          </div>
          
          <div>
            <button
              onClick={() => setShowPasswordForm(!showPasswordForm)}
              className="text-blue-400 hover:text-blue-300 text-sm font-medium"
            >
              {showPasswordForm ? 'Cancel' : 'Change Password'}
            </button>
            
            {showPasswordForm && (
              <form onSubmit={handleChangePassword} className="mt-4 space-y-3">
                <input
                  type="password"
                  placeholder="Current Password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  required
                />
                <input
                  type="password"
                  placeholder="New Password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  required
                />
                <input
                  type="password"
                  placeholder="Confirm New Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  required
                />
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50"
                >
                  Update Password
                </button>
              </form>
            )}
          </div>
        </div>
      </section>

      {/* Upload Platforms Section */}
      <section className="mb-8 bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Upload size={20} />
          Upload Platforms
        </h2>
        
        <div className="space-y-3">
          {['instagram', 'youtube', 'tiktok'].map((platform) => (
            <label key={platform} className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.upload_platforms[platform as keyof typeof settings.upload_platforms]}
                onChange={(e) => setSettings({
                  ...settings,
                  upload_platforms: {
                    ...settings.upload_platforms,
                    [platform]: e.target.checked
                  }
                })}
                className="w-5 h-5 rounded bg-gray-700 border-gray-600 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-white capitalize">{platform}</span>
            </label>
          ))}
        </div>
      </section>

      {/* Directories Section */}
      <section className="mb-8 bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Folder size={20} />
          Directories
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Watch Directory</label>
            <input
              type="text"
              value={settings.directories.watch_dir}
              onChange={(e) => setSettings({
                ...settings,
                directories: { ...settings.directories, watch_dir: e.target.value }
              })}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-1">Processed Directory</label>
            <input
              type="text"
              value={settings.directories.processed_dir}
              onChange={(e) => setSettings({
                ...settings,
                directories: { ...settings.directories, processed_dir: e.target.value }
              })}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            />
          </div>
        </div>
      </section>

      {/* Scheduling Section */}
      <section className="mb-8 bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Clock size={20} />
          Scheduling
        </h2>
        
        <div className="space-y-4">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={settings.scheduling.auto_schedule}
              onChange={(e) => setSettings({
                ...settings,
                scheduling: { ...settings.scheduling, auto_schedule: e.target.checked }
              })}
              className="w-5 h-5 rounded bg-gray-700 border-gray-600 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-white">Enable Auto-Scheduling</span>
          </label>
          
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Post Spacing (hours between posts on same platform)
            </label>
            <input
              type="number"
              min="1"
              value={settings.scheduling.schedule_spacing_hours}
              onChange={(e) => setSettings({
                ...settings,
                scheduling: { ...settings.scheduling, schedule_spacing_hours: parseInt(e.target.value) }
              })}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-400 mb-1">
              Default Post Time (hours after processing)
            </label>
            <input
              type="number"
              min="0"
              value={settings.scheduling.default_post_time_offset}
              onChange={(e) => setSettings({
                ...settings,
                scheduling: { ...settings.scheduling, default_post_time_offset: parseInt(e.target.value) }
              })}
              className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
            />
          </div>
        </div>
      </section>

      {/* Save Button */}
      <button
        onClick={handleSaveSettings}
        disabled={saving}
        className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50"
      >
        <Save size={20} />
        {saving ? 'Saving...' : 'Save Settings'}
      </button>
    </div>
  );
};

export default SettingsPage;
