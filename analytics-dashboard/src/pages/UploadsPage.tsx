import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Play, X, RefreshCw, AlertTriangle, Trash2, Upload, CheckSquare, Square, Video, FastForward, CheckCircle, Edit } from 'lucide-react';
import { uploadsApi, ScheduledPost, FailedUpload, CompletedUpload } from '../services/uploadsApi';
import { missedReplaysApi, MissedReplay } from '../services/missedReplaysApi.ts';
import { VideoPlayer } from '../components/VideoPlayer';
import { UploadsLoading } from '../components/LoadingSpinner';

const UploadsPage: React.FC = () => {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [failedUploads, setFailedUploads] = useState<FailedUpload[]>([]);
  const [missedReplays, setMissedReplays] = useState<MissedReplay[]>([]);
  const [completedUploads, setCompletedUploads] = useState<CompletedUpload[]>([]);
  const [selectedReplays, setSelectedReplays] = useState<Set<string>>(new Set());
  const [selectedVideo, setSelectedVideo] = useState<{ id: number; title: string } | null>(null);
  const [selectedMissedVideo, setSelectedMissedVideo] = useState<{ filePath: string; filename: string } | null>(null);
  const [showLinksModal, setShowLinksModal] = useState<{ upload: CompletedUpload } | null>(null);
  const [activeTab, setActiveTab] = useState<'scheduled' | 'completed' | 'failed' | 'missed'>('scheduled');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [schedulingInProgress, setSchedulingInProgress] = useState(false);
  const [showDateTimePicker, setShowDateTimePicker] = useState<string | null>(null);
  const [selectedDateTime, setSelectedDateTime] = useState<string>('');
  const [editingPost, setEditingPost] = useState<number | null>(null);
  const [editForm, setEditForm] = useState<{
    title: string;
    caption: string;
    hashtags: string;
    platforms: string[];
  }>({ title: '', caption: '', hashtags: '', platforms: [] });

  useEffect(() => {
    loadData();
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setError(null);
      const [postsData, failedData, replaysData, completedData] = await Promise.all([
        uploadsApi.getUpcoming(48),
        uploadsApi.getFailedUploads(),
        missedReplaysApi.getMissedReplays(),
        uploadsApi.getCompleted(7)
      ]);
      setPosts(postsData);
      setFailedUploads(failedData.failed_uploads || []);
      setMissedReplays(replaysData);
      setCompletedUploads(completedData);
    } catch (err) {
      setError('Failed to load uploads');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleForcePost = async (postId: number) => {
    if (!confirm('Post this video immediately?')) return;
    
    try {
      await uploadsApi.forcePostNow(postId);
      setMessage({ type: 'success', text: 'Post queued for immediate posting' });
      loadData();
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to force post' });
    }
  };

  const handleCancel = async (postId: number) => {
    if (!confirm('Cancel this scheduled post?')) return;
    
    try {
      await uploadsApi.cancelPost(postId);
      setMessage({ type: 'success', text: 'Post cancelled successfully' });
      loadData();
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to cancel post' });
    }
  };

  const handleStartEdit = (post: ScheduledPost) => {
    setEditingPost(post.id);
    setEditForm({
      title: post.metadata.title || '',
      caption: post.metadata.caption || '',
      hashtags: post.metadata.hashtags || '',
      platforms: [...post.platforms]
    });
  };

  const handleCancelEdit = () => {
    setEditingPost(null);
    setEditForm({ title: '', caption: '', hashtags: '', platforms: [] });
  };

  const handleSaveEdit = async (postId: number) => {
    try {
      await uploadsApi.updateMetadata(postId, editForm);
      setMessage({ type: 'success', text: 'Metadata updated successfully' });
      setEditingPost(null);
      loadData();
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to update metadata' });
    }
  };

  const togglePlatform = (platform: string) => {
    setEditForm(prev => ({
      ...prev,
      platforms: prev.platforms.includes(platform)
        ? prev.platforms.filter(p => p !== platform)
        : [...prev.platforms, platform]
    }));
  };

  const handleRetry = async (uploadKey: string) => {
    try {
      setMessage(null);
      const result = await uploadsApi.retryUpload(uploadKey);
      if (result.success) {
        setMessage({ type: 'success', text: `Successfully retried ${result.platform.toUpperCase()} upload!` });
        loadData();
      } else {
        setMessage({ type: 'error', text: `Retry failed: ${result.error}` });
      }
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to retry upload' });
    }
  };

  const handleRetryAll = async () => {
    if (!confirm('Retry all failed uploads?')) return;
    
    try {
      setMessage(null);
      const result = await uploadsApi.retryAll();
      setMessage({ 
        type: result.successful > 0 ? 'success' : 'error', 
        text: result.message 
      });
      loadData();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to retry uploads' });
    }
  };

  const handleRemove = async (uploadKey: string) => {
    if (!confirm('Remove this failed upload from the queue?')) return;
    
    try {
      await uploadsApi.removeFailedUpload(uploadKey);
      setMessage({ type: 'success', text: 'Removed from failed uploads' });
      loadData();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to remove upload' });
    }
  };

  // Missed Replays handlers
  const toggleReplaySelection = (filePath: string) => {
    const newSelection = new Set(selectedReplays);
    if (newSelection.has(filePath)) {
      newSelection.delete(filePath);
    } else {
      newSelection.add(filePath);
    }
    setSelectedReplays(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedReplays.size === missedReplays.length) {
      setSelectedReplays(new Set());
    } else {
      setSelectedReplays(new Set(missedReplays.map(r => r.file_path)));
    }
  };

  const handleScheduleNext = async (videoPath: string) => {
    setSchedulingInProgress(true);
    try {
      const result = await missedReplaysApi.scheduleReplay(videoPath);
      setMessage({ 
        type: 'success', 
        text: `Scheduled "${result.metadata.title}" for ${new Date(result.scheduled_time).toLocaleString()}` 
      });
      setSelectedReplays(new Set()); // Clear selection
      loadData();
    } catch (err: any) {
      let errorText = 'Failed to schedule replay';
      if (err.message) {
        errorText = err.message;
      } else if (typeof err === 'string') {
        errorText = err;
      } else if (Array.isArray(err)) {
        errorText = err.map(e => typeof e === 'string' ? e : e.message || e.toString()).join(', ');
      } else {
        errorText = err.toString();
      }
      setMessage({ type: 'error', text: errorText });
    } finally {
      setSchedulingInProgress(false);
    }
  };

  const handleScheduleWithTime = async (videoPath: string, dateTime: string) => {
    setSchedulingInProgress(true);
    try {
      const result = await missedReplaysApi.scheduleReplay(videoPath, dateTime);
      setMessage({ 
        type: 'success', 
        text: `Scheduled "${result.metadata.title}" for ${new Date(result.scheduled_time).toLocaleString()}` 
      });
      setShowDateTimePicker(null);
      setSelectedReplays(new Set());
      loadData();
    } catch (err: any) {
      let errorText = 'Failed to schedule replay';
      if (err.message) {
        errorText = err.message;
      } else if (typeof err === 'string') {
        errorText = err;
      } else if (Array.isArray(err)) {
        errorText = err.map(e => typeof e === 'string' ? e : e.message || e.toString()).join(', ');
      } else {
        errorText = err.toString();
      }
      setMessage({ type: 'error', text: errorText });
    } finally {
      setSchedulingInProgress(false);
    }
  };

  const handleScheduleSelected = async () => {
    if (selectedReplays.size === 0) return;
    if (!confirm(`Schedule ${selectedReplays.size} video(s)? They will be spaced 1 hour apart.`)) return;
    
    setSchedulingInProgress(true);
    try {
      const result = await missedReplaysApi.scheduleBatch(Array.from(selectedReplays));
      setMessage({ 
        type: result.successful > 0 ? 'success' : 'error',
        text: `Scheduled ${result.successful} of ${result.total} videos. ${result.failed > 0 ? `${result.failed} failed.` : ''}`
      });
      setSelectedReplays(new Set());
      loadData();
    } catch (err: any) {
      let errorText = 'Failed to schedule batch';
      if (err.message) {
        errorText = err.message;
      } else if (typeof err === 'string') {
        errorText = err;
      } else if (Array.isArray(err)) {
        errorText = err.map(e => typeof e === 'string' ? e : e.message || e.toString()).join(', ');
      } else {
        errorText = err.toString();
      }
      setMessage({ type: 'error', text: errorText });
    } finally {
      setSchedulingInProgress(false);
    }
  };

  const openDateTimePicker = (videoPath: string) => {
    // Set default to next hour
    const nextHour = new Date();
    nextHour.setHours(nextHour.getHours() + 1, 0, 0, 0);
    const isoString = nextHour.toISOString().slice(0, 16);
    setSelectedDateTime(isoString);
    setShowDateTimePicker(videoPath);
  };

  const getCountdown = (scheduledTime: string) => {
    const now = new Date();
    const target = new Date(scheduledTime);
    const diff = target.getTime() - now.getTime();
    
    if (diff <= 0) return 'Posting now...';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `in ${days}d ${hours % 24}h`;
    }
    
    return `in ${hours}h ${minutes}m`;
  };

  const getRelativeTime = (timestamp: string) => {
    const now = new Date();
    const past = new Date(timestamp);
    const diff = now.getTime() - past.getTime();
    
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'just now';
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      processing: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      completed: 'bg-green-500/20 text-green-400 border-green-500/30',
      failed: 'bg-red-500/20 text-red-400 border-red-500/30',
      cancelled: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full border ${styles[status as keyof typeof styles] || styles.pending}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  const getPlatformBadge = (platform: string) => {
    const styles = {
      youtube: 'bg-red-500/20 text-red-400 border-red-500/30',
      instagram: 'bg-pink-500/20 text-pink-400 border-pink-500/30',
      tiktok: 'bg-gray-500/20 text-white border-gray-500/30',
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded border ${styles[platform as keyof typeof styles] || 'bg-gray-500/20 text-gray-400 border-gray-500/30'}`}>
        {platform.toUpperCase()}
      </span>
    );
  };

  const formatFileSize = (bytes: number) => {
    return (bytes / (1024 * 1024)).toFixed(1);
  };

  const formatTimeSince = (timestamp: number) => {
    const now = Date.now();
    const diff = now - (timestamp * 1000);
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'just now';
  };

  const pendingCount = posts.filter(p => p.status === 'pending').length;
  const todayCount = posts.filter(p => {
    const today = new Date().toDateString();
    return new Date(p.scheduled_time).toDateString() === today;
  }).length;
  const failedCount = failedUploads.length;
  const missedCount = missedReplays.length;

  if (loading) {
    return <UploadsLoading fullScreen />;
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-2">
          <Upload size={32} />
          Uploads
        </h1>
        <p className="text-gray-400">Manage scheduled and failed uploads</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Total Scheduled</div>
          <div className="text-2xl font-bold text-white">{pendingCount}</div>
        </div>
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Posting Today</div>
          <div className="text-2xl font-bold text-white">{todayCount}</div>
        </div>
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Missed Replays</div>
          <div className="text-2xl font-bold text-yellow-400">{missedCount}</div>
        </div>
        <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Failed Uploads</div>
          <div className="text-2xl font-bold text-red-400">{failedCount}</div>
        </div>
      </div>

      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-900/50 text-green-200' : 'bg-red-900/50 text-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-4 rounded-lg mb-4">
          {error}
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 border-b border-gray-700">
        <button
          onClick={() => setActiveTab('scheduled')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'scheduled' 
              ? 'text-blue-400 border-b-2 border-blue-400' 
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Scheduled ({pendingCount})
        </button>
        <button
          onClick={() => setActiveTab('completed')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'completed' 
              ? 'text-green-400 border-b-2 border-green-400' 
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Successful ({completedUploads.length})
        </button>
        <button
          onClick={() => setActiveTab('failed')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'failed' 
              ? 'text-red-400 border-b-2 border-red-400' 
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Failed ({failedCount})
        </button>
        <button
          onClick={() => setActiveTab('missed')}
          className={`px-4 py-2 font-medium transition-colors ${
            activeTab === 'missed' 
              ? 'text-yellow-400 border-b-2 border-yellow-400' 
              : 'text-gray-400 hover:text-white'
          }`}
        >
          Missed Replays ({missedCount})
        </button>
      </div>

      {/* Scheduled Uploads Section */}
      {activeTab === 'scheduled' && (
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <Calendar size={20} />
          Scheduled Uploads ({pendingCount})
        </h2>
        
        <div className="space-y-4">
          {posts.length === 0 ? (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-12 text-center">
              <Calendar size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">No scheduled posts</p>
              <p className="text-sm text-gray-500 mt-2">
                Videos will appear here when processed by the watcher
              </p>
            </div>
          ) : (
            posts.map((post) => (
              <div key={post.id} className="bg-gray-900 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-white font-semibold">{post.metadata.title}</h3>
                      {getStatusBadge(post.status)}
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-400 mb-3">
                      <div className="flex items-center gap-1">
                        <Clock size={14} />
                        <span>{new Date(post.scheduled_time).toLocaleString()}</span>
                      </div>
                      {post.status === 'pending' && (
                        <span className="text-blue-400 font-semibold">
                          {getCountdown(post.scheduled_time)}
                        </span>
                      )}
                    </div>
                    
                    <div className="flex gap-2">
                      {post.platforms.map((platform) => (
                        <span
                          key={platform}
                          className="px-2 py-1 bg-gray-800 text-gray-300 text-xs rounded"
                        >
                          {platform.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex gap-2">
                    {post.status === 'pending' && (
                      <>
                        <button
                          onClick={() => handleStartEdit(post)}
                          className="px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                        >
                          <Edit size={14} />
                          Edit
                        </button>
                        <button
                          onClick={() => handleForcePost(post.id)}
                          className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                        >
                          <Play size={14} />
                          Post Now
                        </button>
                        <button
                          onClick={() => handleCancel(post.id)}
                          className="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                        >
                          <X size={14} />
                          Cancel
                        </button>
                      </>
                    )}
                    {post.status === 'failed' && (
                      <button
                        onClick={() => handleForcePost(post.id)}
                        className="px-3 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                      >
                        <RefreshCw size={14} />
                        Retry
                      </button>
                    )}
                  </div>
                </div>
                
                {/* Expandable Edit Form */}
                {editingPost === post.id && (
                  <div className="mt-4 p-4 bg-gray-800 border border-gray-600 rounded-lg animate-in slide-in-from-top-2 duration-200">
                    <h4 className="text-white font-medium mb-4">Edit Metadata</h4>
                    
                    <div className="space-y-4">
                      {/* Title */}
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Title</label>
                        <input
                          type="text"
                          value={editForm.title}
                          onChange={(e) => setEditForm(prev => ({ ...prev, title: e.target.value }))}
                          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                          placeholder="Video title"
                        />
                      </div>
                      
                      {/* Caption */}
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Caption</label>
                        <textarea
                          value={editForm.caption}
                          onChange={(e) => setEditForm(prev => ({ ...prev, caption: e.target.value }))}
                          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 h-24 resize-none"
                          placeholder="Video description/caption"
                        />
                      </div>
                      
                      {/* Hashtags */}
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Hashtags</label>
                        <input
                          type="text"
                          value={editForm.hashtags}
                          onChange={(e) => setEditForm(prev => ({ ...prev, hashtags: e.target.value }))}
                          className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
                          placeholder="#hashtag1 #hashtag2 #hashtag3"
                        />
                      </div>
                      
                      {/* Platforms */}
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Platforms</label>
                        <div className="flex gap-4">
                          {['youtube', 'instagram', 'tiktok'].map((platform) => (
                            <label key={platform} className="flex items-center gap-2 cursor-pointer">
                              <input
                                type="checkbox"
                                checked={editForm.platforms.includes(platform)}
                                onChange={() => togglePlatform(platform)}
                                className="w-4 h-4 text-blue-600 bg-gray-800 border-gray-700 rounded focus:ring-blue-500 focus:ring-2"
                              />
                              <span className="text-white text-sm capitalize">{platform}</span>
                            </label>
                          ))}
                        </div>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex gap-3 justify-end pt-2">
                        <button
                          onClick={handleCancelEdit}
                          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => handleSaveEdit(post.id)}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
                        >
                          Save Changes
                        </button>
                      </div>
                    </div>
                  </div>
                )}
                
                {post.error_message && (
                  <div className="mt-3 p-2 bg-red-500/10 border border-red-500/30 rounded text-xs text-red-400">
                    {post.error_message}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
      )}

      {/* Failed Uploads Section */}
      {activeTab === 'failed' && (
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <AlertTriangle size={20} className="text-red-400" />
            Failed Uploads ({failedCount})
          </h2>
          {failedCount > 0 && (
            <button
              onClick={handleRetryAll}
              className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
            >
              <RefreshCw size={16} />
              Retry All
            </button>
          )}
        </div>
        
        <div className="space-y-4">
          {failedUploads.length === 0 ? (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-12 text-center">
              <AlertTriangle size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">No failed uploads</p>
              <p className="text-sm text-gray-500 mt-2">
                Failed uploads will appear here for retry
              </p>
            </div>
          ) : (
            failedUploads.map((upload) => {
              const videoName = upload.video_path.split(/[\\/]/).pop() || 'Unknown';
              return (
                <div key={upload.key} className="bg-gray-900 border border-red-500/30 rounded-lg p-6 hover:border-red-500/50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-white font-semibold">{upload.metadata.title || videoName}</h3>
                        {getPlatformBadge(upload.platform)}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-400 mb-3">
                        <span>Failed: {getRelativeTime(upload.timestamp)}</span>
                        <span>Retries: {upload.retry_count}</span>
                      </div>
                      
                      <div className="bg-red-500/10 border border-red-500/30 rounded p-2 text-xs text-red-400">
                        <strong>Error:</strong> {upload.error}
                      </div>
                    </div>
                    
                    <div className="flex gap-2 ml-4">
                      <button
                        onClick={() => handleRetry(upload.key)}
                        className="px-3 py-2 bg-yellow-600 hover:bg-yellow-700 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                      >
                        <RefreshCw size={14} />
                        Retry
                      </button>
                      <button
                        onClick={() => handleRemove(upload.key)}
                        className="px-3 py-2 bg-gray-800 hover:bg-gray-700 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                      >
                        <Trash2 size={14} />
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
      )}

      {/* Missed Replays Section */}
      {activeTab === 'missed' && (
      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white flex items-center gap-2">
            <Video size={20} className="text-yellow-400" />
            Missed Replays ({missedCount})
          </h2>
          {missedCount > 0 && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-400">
                {selectedReplays.size} selected
              </span>
              <button
                onClick={handleScheduleSelected}
                disabled={selectedReplays.size === 0 || schedulingInProgress}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
              >
                <FastForward size={16} />
                Schedule Selected
              </button>
            </div>
          )}
        </div>
        
        <div className="space-y-4">
          {missedReplays.length === 0 ? (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-12 text-center">
              <Video size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">No missed replays</p>
              <p className="text-sm text-gray-500 mt-2">
                Replays not processed while the watcher was down will appear here
              </p>
            </div>
          ) : (
            <>
              {/* Select All Row */}
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                <div className="flex items-center gap-3">
                  <button
                    onClick={toggleSelectAll}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    {selectedReplays.size === missedReplays.length ? (
                      <CheckSquare size={20} />
                    ) : (
                      <Square size={20} />
                    )}
                  </button>
                  <span className="text-sm text-gray-400">
                    {selectedReplays.size === missedReplays.length ? 'Deselect All' : 'Select All'}
                  </span>
                </div>
              </div>

              {/* Replay List */}
              {missedReplays.map((replay) => (
                <div 
                  key={replay.file_path} 
                  className={`bg-gradient-to-br from-gray-900 to-gray-800 border rounded-xl p-6 hover:border-gray-500 hover:shadow-xl hover:shadow-yellow-500/10 transition-all duration-300 ${
                    selectedReplays.has(replay.file_path) ? 'border-yellow-500 shadow-lg shadow-yellow-500/20' : 'border-gray-700'
                  }`}
                >
                  <div className="flex items-start gap-6">
                    {/* Selection Checkbox */}
                    <button
                      onClick={() => toggleReplaySelection(replay.file_path)}
                      className="text-gray-400 hover:text-white transition-colors mt-1"
                    >
                      {selectedReplays.has(replay.file_path) ? (
                        <CheckSquare size={24} className="text-yellow-400" />
                      ) : (
                        <Square size={24} />
                      )}
                    </button>
                    
                    {/* Video Preview Thumbnail */}
                    <div className="relative w-32 h-20 bg-gray-800 rounded-lg overflow-hidden flex-shrink-0">
                      <video 
                        src={missedReplaysApi.getVideoUrl(replay.file_path)}
                        className="w-full h-full object-cover"
                        preload="metadata"
                        muted
                      />
                      <button
                        onClick={() => setSelectedMissedVideo({ filePath: replay.file_path, filename: replay.filename })}
                        className="absolute inset-0 flex items-center justify-center bg-black/50 hover:bg-black/30 transition-colors group"
                      >
                        <Play size={20} className="text-white group-hover:scale-110 transition-transform" />
                      </button>
                    </div>
                    
                    {/* Video Info */}
                    <div className="flex-1 min-w-0">
                      <h3 className="text-white font-semibold mb-2 text-lg truncate">{replay.filename}</h3>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-400 mb-3">
                        <span className="flex items-center gap-1">
                          <Video size={12} />
                          {formatFileSize(replay.file_size)} MB
                        </span>
                        <span>•</span>
                        <span>Modified {formatTimeSince(replay.modified_time)}</span>
                      </div>
                      
                      {/* File Path */}
                      <div className="text-xs text-gray-500 bg-gray-800/50 rounded px-2 py-1 inline-block max-w-full truncate">
                        {replay.file_path}
                      </div>
                    </div>
                    
                    {/* Action Buttons */}
                    <div className="flex gap-2 flex-shrink-0">
                      <button
                        onClick={() => setSelectedMissedVideo({ filePath: replay.file_path, filename: replay.filename })}
                        className="px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                      >
                        <Play size={14} />
                        Preview
                      </button>
                      <button
                        onClick={() => handleScheduleNext(replay.file_path)}
                        disabled={schedulingInProgress}
                        className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                      >
                        <FastForward size={14} />
                        Schedule Next
                      </button>
                      <button
                        onClick={() => openDateTimePicker(replay.file_path)}
                        disabled={schedulingInProgress}
                        className="px-3 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
                      >
                        <Calendar size={14} />
                        Pick Time
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>
      </div>
      )}

      {/* Successful Uploads Section */}
      {activeTab === 'completed' && (
        <div>
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <CheckCircle size={20} className="text-green-400" />
            Successful Uploads (Last 7 Days)
          </h2>
          
          {completedUploads.length === 0 ? (
            <div className="bg-gray-900 border border-gray-700 rounded-lg p-12 text-center">
              <CheckCircle size={48} className="mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">No completed uploads yet</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {completedUploads.map((upload) => (
                <div key={upload.id} className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-xl overflow-hidden hover:border-gray-500 hover:shadow-2xl hover:shadow-purple-500/10 transition-all duration-300 group">
                  {/* Video Thumbnail with Enhanced Overlay */}
                  <div className="relative aspect-video bg-gray-800 overflow-hidden">
                    <video 
                      src={uploadsApi.getVideoUrl(upload.id)}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      preload="metadata"
                      muted
                    />
                    {/* Enhanced Play Button Overlay */}
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <button
                        onClick={() => setSelectedVideo({ id: upload.id, title: upload.metadata.title })}
                        className="absolute inset-0 flex items-center justify-center"
                      >
                        <div className="bg-white/20 backdrop-blur-sm rounded-full p-4 hover:bg-white/30 transition-colors">
                          <Play size={32} className="text-white ml-1" />
                        </div>
                      </button>
                    </div>
                    
                    {/* Video Duration Badge */}
                    <div className="absolute top-3 right-3 bg-black/70 backdrop-blur-sm text-white text-xs px-2 py-1 rounded">
                      <Clock size={10} className="inline mr-1" />
                      {new Date(upload.processed_at).toLocaleDateString()}
                    </div>
                    
                    {/* Platform Icons Overlay */}
                    <div className="absolute bottom-3 left-3 flex gap-2">
                      {upload.platforms.map((platform) => (
                        <div
                          key={platform}
                          className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                            platform === 'youtube' ? 'bg-red-500' :
                            platform === 'instagram' ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                            platform === 'tiktok' ? 'bg-black' :
                            'bg-gray-500'
                          }`}
                        >
                          {platform === 'youtube' ? 'YT' :
                           platform === 'instagram' ? 'IG' :
                           platform === 'tiktok' ? 'TT' : platform.charAt(0).toUpperCase()}
                        </div>
                      ))}
                    </div>
                  </div>
                  
                  {/* Enhanced Video Info */}
                  <div className="p-5">
                    <h3 className="text-white font-semibold mb-3 line-clamp-2 text-lg group-hover:text-purple-300 transition-colors">
                      {upload.metadata.title}
                    </h3>
                    
                    {/* Enhanced Platform Badges */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {upload.platforms.map((platform) => (
                        <span
                          key={platform}
                          className={`px-3 py-1 text-xs font-medium rounded-full border ${
                            platform === 'youtube' ? 'bg-red-500/20 text-red-400 border-red-500/30' :
                            platform === 'instagram' ? 'bg-pink-500/20 text-pink-400 border-pink-500/30' :
                            platform === 'tiktok' ? 'bg-gray-500/20 text-gray-300 border-gray-500/30' :
                            'bg-gray-500/20 text-gray-400 border-gray-500/30'
                          }`}
                        >
                          {platform.toUpperCase()}
                        </span>
                      ))}
                    </div>
                    
                    {/* Enhanced Action Buttons */}
                    <div className="flex gap-2">
                      <button 
                        onClick={() => setSelectedVideo({ id: upload.id, title: upload.metadata.title })}
                        className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white text-sm font-medium rounded-lg transition-all duration-200 hover:shadow-lg hover:shadow-purple-500/25 flex items-center justify-center gap-2"
                      >
                        <Play size={16} />
                        Preview
                      </button>
                      <button 
                        onClick={() => setShowLinksModal({ upload })}
                        className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors flex items-center gap-2"
                      >
                        <Upload size={16} />
                        Links
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* DateTime Picker Modal */}
      {showDateTimePicker && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-white mb-4">Schedule Video</h3>
            
            <div className="mb-4">
              <label className="block text-sm text-gray-400 mb-2">
                Select Date and Time
              </label>
              <input
                type="datetime-local"
                value={selectedDateTime}
                onChange={(e) => setSelectedDateTime(e.target.value)}
                className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDateTimePicker(null)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => handleScheduleWithTime(showDateTimePicker, selectedDateTime)}
                disabled={schedulingInProgress || !selectedDateTime}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              >
                {schedulingInProgress ? 'Scheduling...' : 'Schedule'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Video Player Modal */}
      {selectedVideo && (
        <VideoPlayer
          videoUrl={uploadsApi.getVideoUrl(selectedVideo.id)}
          title={selectedVideo.title}
          onClose={() => setSelectedVideo(null)}
        />
      )}

      {/* Missed Video Player Modal */}
      {selectedMissedVideo && (
        <VideoPlayer
          videoUrl={missedReplaysApi.getVideoUrl(selectedMissedVideo.filePath)}
          title={selectedMissedVideo.filename}
          onClose={() => setSelectedMissedVideo(null)}
        />
      )}

      {/* Platform Links Modal */}
      {showLinksModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Platform Links</h3>
              <button
                onClick={() => setShowLinksModal(null)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="mb-4">
              <h4 className="text-lg font-medium text-white mb-2">{showLinksModal.upload.metadata.title}</h4>
              <p className="text-gray-400 text-sm">Posted on {new Date(showLinksModal.upload.processed_at).toLocaleDateString()}</p>
            </div>
            
            <div className="space-y-4">
              {showLinksModal.upload.platforms.map((platform) => {
                const platformUrl = showLinksModal.upload.platform_urls?.[platform];
                return (
                  <div key={platform} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold ${
                            platform === 'youtube' ? 'bg-red-500' :
                            platform === 'instagram' ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                            platform === 'tiktok' ? 'bg-black' :
                            'bg-gray-500'
                          }`}
                        >
                          {platform === 'youtube' ? 'YT' :
                           platform === 'instagram' ? 'IG' :
                           platform === 'tiktok' ? 'TT' : platform.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <h5 className="text-white font-medium">{platform.charAt(0).toUpperCase() + platform.slice(1)}</h5>
                          {platformUrl?.video_id && (
                            <p className="text-gray-400 text-sm">ID: {platformUrl.video_id}</p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        {platformUrl?.url ? (
                          <a
                            href={platformUrl.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors flex items-center gap-2"
                          >
                            <Upload size={16} />
                            View Post
                          </a>
                        ) : (
                          <div className="px-4 py-2 bg-gray-700 text-gray-400 text-sm rounded-lg flex items-center gap-2">
                            <X size={16} />
                            No URL Available
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {Object.keys(showLinksModal.upload.platform_urls || {}).length === 0 && (
              <div className="text-center py-8">
                <Upload size={48} className="mx-auto text-gray-600 mb-4" />
                <p className="text-gray-400">No platform URLs available for this video</p>
                <p className="text-gray-500 text-sm mt-2">URLs will appear here once the video is successfully uploaded to each platform</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadsPage;

