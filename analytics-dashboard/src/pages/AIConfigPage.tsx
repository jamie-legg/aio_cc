import React, { useState, useEffect } from 'react';
import { Plus, Save, Trash2, Check, Sparkles, Play } from 'lucide-react';
import { aiConfigApi, AITemplate } from '../services/aiConfigApi';
import { AIConfigLoading } from '../components/LoadingSpinner';

const DEFAULT_TEMPLATE = `You are a social media expert creating engaging content for gaming videos.

Given a video filename: {filename}
Game context: {game_context}

Generate:
1. An exciting, click-worthy title (max 100 chars)
2. An engaging caption with emojis (max 2200 chars)
3. 10-15 relevant hashtags

Format as JSON:
{
  "title": "...",
  "caption": "...",
  "hashtags": "#gaming #..."
}`;

const AIConfigPage: React.FC = () => {
  const [templates, setTemplates] = useState<AITemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<AITemplate | null>(null);
  const [name, setName] = useState('');
  const [promptText, setPromptText] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testModalOpen, setTestModalOpen] = useState(false);
  const [testFilename, setTestFilename] = useState('epic_gaming_moment.mp4');
  const [testContext, setTestContext] = useState('gaming');
  const [testResult, setTestResult] = useState<any>(null);
  const [testLoading, setTestLoading] = useState(false);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await aiConfigApi.getTemplates();
      setTemplates(data);
      
      // Select active template or first template
      const active = data.find(t => t.is_active);
      if (active) {
        selectTemplate(active);
      } else if (data.length > 0) {
        selectTemplate(data[0]);
      }
    } catch (err) {
      console.error('Failed to load templates:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectTemplate = (template: AITemplate) => {
    setSelectedTemplate(template);
    setName(template.name);
    setPromptText(template.prompt_text);
  };

  const handleCreate = async () => {
    const newName = prompt('Template name:');
    if (!newName) return;
    
    try {
      setSaving(true);
      await aiConfigApi.createTemplate({
        name: newName,
        prompt_text: DEFAULT_TEMPLATE,
        is_active: false
      });
      await loadTemplates();
    } catch (err) {
      alert('Failed to create template');
    } finally {
      setSaving(false);
    }
  };

  const handleSave = async () => {
    if (!selectedTemplate) return;
    
    try {
      setSaving(true);
      await aiConfigApi.updateTemplate(selectedTemplate.id, {
        name,
        prompt_text: promptText
      });
      await loadTemplates();
      alert('Template saved!');
    } catch (err) {
      alert('Failed to save template');
    } finally {
      setSaving(false);
    }
  };

  const handleActivate = async () => {
    if (!selectedTemplate) return;
    
    try {
      setSaving(true);
      await aiConfigApi.activateTemplate(selectedTemplate.id);
      await loadTemplates();
    } catch (err) {
      alert('Failed to activate template');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedTemplate) return;
    if (!confirm(`Delete template "${selectedTemplate.name}"?`)) return;
    
    try {
      setSaving(true);
      await aiConfigApi.deleteTemplate(selectedTemplate.id);
      await loadTemplates();
      setSelectedTemplate(null);
      setName('');
      setPromptText('');
    } catch (err) {
      alert('Failed to delete template');
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTestLoading(true);
    try {
      const result = await aiConfigApi.testPrompt({
        prompt_text: promptText,
        filename: testFilename,
        game_context: testContext
      });
      setTestResult(result.metadata);
    } catch (err) {
      alert('Failed to test prompt');
    } finally {
      setTestLoading(false);
    }
  };

  if (loading) {
    return <AIConfigLoading fullScreen />;
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">AI Configuration</h1>
        <p className="text-gray-400">Manage AI prompt templates for metadata generation</p>
      </div>

      <div className="grid grid-cols-5 gap-6">
        {/* Template List */}
        <div className="col-span-2 space-y-4">
          <button
            onClick={handleCreate}
            className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center justify-center gap-2 transition-colors"
          >
            <Plus size={20} />
            New Template
          </button>

          <div className="space-y-2">
            {templates.length === 0 ? (
              <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 text-center text-gray-400">
                No templates yet
              </div>
            ) : (
              templates.map((template) => (
                <div
                  key={template.id}
                  onClick={() => selectTemplate(template)}
                  className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                    selectedTemplate?.id === template.id
                      ? 'bg-gray-800 border-blue-500'
                      : 'bg-gray-900 border-gray-700 hover:border-gray-600'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-white font-semibold">{template.name}</h3>
                    {template.is_active && (
                      <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full border border-green-500/30 flex items-center gap-1">
                        <Check size={10} />
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-gray-400 text-sm line-clamp-2">
                    {template.prompt_text.substring(0, 100)}...
                  </p>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Template Editor */}
        <div className="col-span-3 space-y-4">
          {selectedTemplate ? (
            <>
              <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
                <label className="block text-sm text-gray-400 mb-2">Template Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="bg-gray-900 border border-gray-700 rounded-lg p-6">
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm text-gray-400">Prompt Text</label>
                  <span className="text-xs text-gray-500">
                    Variables: {'{filename}'}, {'{game_context}'}
                  </span>
                </div>
                <textarea
                  value={promptText}
                  onChange={(e) => setPromptText(e.target.value)}
                  rows={20}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white font-mono text-sm focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleSave}
                  disabled={saving}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
                >
                  <Save size={16} />
                  {saving ? 'Saving...' : 'Save'}
                </button>
                
                {!selectedTemplate.is_active && (
                  <button
                    onClick={handleActivate}
                    disabled={saving}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
                  >
                    <Check size={16} />
                    Set as Active
                  </button>
                )}
                
                <button
                  onClick={() => setTestModalOpen(true)}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"
                >
                  <Sparkles size={16} />
                  Test Prompt
                </button>
                
                <button
                  onClick={handleDelete}
                  disabled={saving}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 ml-auto"
                >
                  <Trash2 size={16} />
                  Delete
                </button>
              </div>
            </>
          ) : (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-12 text-center">
              <Sparkles size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">Select a template to edit</p>
            </div>
          )}
        </div>
      </div>

      {/* Test Modal */}
      {testModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-[600px] max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold text-white mb-4">Test Prompt</h2>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Sample Filename</label>
                <input
                  type="text"
                  value={testFilename}
                  onChange={(e) => setTestFilename(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-2">Game Context</label>
                <input
                  type="text"
                  value={testContext}
                  onChange={(e) => setTestContext(e.target.value)}
                  className="w-full px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                />
              </div>
              
              <button
                onClick={handleTest}
                disabled={testLoading}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
              >
                <Play size={16} />
                {testLoading ? 'Generating...' : 'Generate'}
              </button>
            </div>
            
            {testResult && (
              <div className="space-y-3 mb-6">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Title</label>
                  <div className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white">
                    {testResult.title}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Caption</label>
                  <div className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white max-h-40 overflow-y-auto">
                    {testResult.caption}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Hashtags</label>
                  <div className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white">
                    {testResult.hashtags}
                  </div>
                </div>
              </div>
            )}
            
            <button
              onClick={() => {
                setTestModalOpen(false);
                setTestResult(null);
              }}
              className="w-full px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIConfigPage;

