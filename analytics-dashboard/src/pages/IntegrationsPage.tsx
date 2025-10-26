import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Edit, TestTube, Webhook, Save, X } from 'lucide-react';
import { integrationsApi, DiscordWebhook, DiscordWebhookCreateRequest } from '../services/integrationsApi';
import { IntegrationsLoading } from '../components/LoadingSpinner';

const IntegrationsPage: React.FC = () => {
  const [webhooks, setWebhooks] = useState<DiscordWebhook[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  
  // Form state
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingWebhook, setEditingWebhook] = useState<DiscordWebhook | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    platforms: [] as string[]
  });

  const availablePlatforms = [
    { id: 'youtube', name: 'YouTube', emoji: '🎬' },
    { id: 'instagram', name: 'Instagram', emoji: '📸' },
    { id: 'tiktok', name: 'TikTok', emoji: '🎵' }
  ];

  useEffect(() => {
    loadWebhooks();
  }, []);

  const loadWebhooks = async () => {
    try {
      setLoading(true);
      const response = await integrationsApi.listDiscordWebhooks();
      setWebhooks(response.webhooks);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load webhooks' });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage(null);

    try {
      if (editingWebhook) {
        // Update existing webhook
        await integrationsApi.updateDiscordWebhook(editingWebhook.id, formData);
        setMessage({ type: 'success', text: 'Webhook updated successfully!' });
      } else {
        // Create new webhook
        await integrationsApi.createDiscordWebhook(formData as DiscordWebhookCreateRequest);
        setMessage({ type: 'success', text: 'Webhook created successfully!' });
      }
      
      setShowAddForm(false);
      setEditingWebhook(null);
      setFormData({ name: '', url: '', platforms: [] });
      await loadWebhooks();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to save webhook' });
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (webhookId: string) => {
    if (!confirm('Are you sure you want to delete this webhook?')) return;

    try {
      await integrationsApi.deleteDiscordWebhook(webhookId);
      setMessage({ type: 'success', text: 'Webhook deleted successfully!' });
      await loadWebhooks();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to delete webhook' });
    }
  };

  const handleEdit = (webhook: DiscordWebhook) => {
    setEditingWebhook(webhook);
    setFormData({
      name: webhook.name,
      url: webhook.url,
      platforms: webhook.platforms
    });
    setShowAddForm(true);
  };

  const handleTest = async (webhookUrl: string) => {
    try {
      setMessage(null);
      const result = await integrationsApi.testDiscordWebhook(webhookUrl);
      if (result.success) {
        setMessage({ type: 'success', text: result.message });
      } else {
        setMessage({ type: 'error', text: result.message });
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to test webhook' });
    }
  };

  const handlePlatformChange = (platformId: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      platforms: checked 
        ? [...prev.platforms, platformId]
        : prev.platforms.filter(p => p !== platformId)
    }));
  };

  const cancelForm = () => {
    setShowAddForm(false);
    setEditingWebhook(null);
    setFormData({ name: '', url: '', platforms: [] });
  };

  if (loading) {
    return <IntegrationsLoading fullScreen />;
  }

  return (
    <div className="p-6 max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Webhook size={24} />
          Integrations
        </h1>
        <button
          onClick={() => setShowAddForm(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
        >
          <Plus size={20} />
          Add Webhook
        </button>
      </div>
      
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-900/50 text-green-200' : 'bg-red-900/50 text-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Discord Webhooks Section */}
      <section className="mb-8 bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Webhook size={20} />
          Discord Webhooks
        </h2>
        <p className="text-gray-400 mb-6">
          Configure Discord webhooks to receive notifications when videos are uploaded to social media platforms.
        </p>

        {/* Webhook List */}
        <div className="space-y-4">
          {webhooks.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <Webhook size={48} className="mx-auto mb-4 opacity-50" />
              <p>No Discord webhooks configured</p>
              <p className="text-sm">Add your first webhook to get started</p>
            </div>
          ) : (
            webhooks.map((webhook) => (
              <div key={webhook.id} className="bg-gray-700 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <h3 className="text-white font-medium">{webhook.name}</h3>
                    <p className="text-gray-400 text-sm truncate">{webhook.url}</p>
                    <div className="flex items-center gap-2 mt-2">
                      <span className="text-gray-400 text-sm">Platforms:</span>
                      {webhook.platforms.map((platform) => {
                        const platformInfo = availablePlatforms.find(p => p.id === platform);
                        return (
                          <span key={platform} className="inline-flex items-center gap-1 px-2 py-1 bg-gray-600 text-gray-200 text-xs rounded">
                            {platformInfo?.emoji} {platformInfo?.name || platform}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleTest(webhook.url)}
                      className="p-2 text-blue-400 hover:text-blue-300 hover:bg-gray-600 rounded"
                      title="Test webhook"
                    >
                      <TestTube size={16} />
                    </button>
                    <button
                      onClick={() => handleEdit(webhook)}
                      className="p-2 text-yellow-400 hover:text-yellow-300 hover:bg-gray-600 rounded"
                      title="Edit webhook"
                    >
                      <Edit size={16} />
                    </button>
                    <button
                      onClick={() => handleDelete(webhook.id)}
                      className="p-2 text-red-400 hover:text-red-300 hover:bg-gray-600 rounded"
                      title="Delete webhook"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Add/Edit Form Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-white mb-4">
              {editingWebhook ? 'Edit Webhook' : 'Add Discord Webhook'}
            </h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  placeholder="e.g., YouTube Uploads"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Webhook URL</label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
                  className="w-full px-4 py-2 bg-gray-700 text-white rounded-lg"
                  placeholder="https://discord.com/api/webhooks/..."
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Platforms</label>
                <div className="space-y-2">
                  {availablePlatforms.map((platform) => (
                    <label key={platform.id} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.platforms.includes(platform.id)}
                        onChange={(e) => handlePlatformChange(platform.id, e.target.checked)}
                        className="w-5 h-5 rounded bg-gray-700 border-gray-600 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-white">
                        {platform.emoji} {platform.name}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center gap-3 pt-4">
                <button
                  type="submit"
                  disabled={saving || formData.platforms.length === 0}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50"
                >
                  <Save size={16} />
                  {saving ? 'Saving...' : (editingWebhook ? 'Update' : 'Create')}
                </button>
                <button
                  type="button"
                  onClick={cancelForm}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium"
                >
                  <X size={16} />
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntegrationsPage;

