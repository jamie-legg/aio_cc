import React, { useState, useEffect } from 'react';
import { Calendar, Clock, Play, X, RefreshCw, AlertTriangle, Trash2, Upload, CheckSquare, Square, Video, FastForward } from 'lucide-react';
import { uploadsApi, ScheduledPost, FailedUpload } from '../services/uploadsApi';
import { missedReplaysApi, MissedReplay } from '../services/missedReplaysApi.ts';

const UploadsPage: React.FC = () => {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [failedUploads, setFailedUploads] = useState<FailedUpload[]>([]);
  const [missedReplays, setMissedReplays] = useState<MissedReplay[]>([]);
  const [selectedReplays, setSelectedReplays] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [schedulingInProgress, setSchedulingInProgress] = useState(false);
  const [showDateTimePicker, setShowDateTimePicker] = useState<string | null>(null);
  const [selectedDateTime, setSelectedDateTime] = useState<string>('');

  useEffect(() => {
    loadData();
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      setError(null);
      const [postsData, failedData, replaysData] = await Promise.all([
        uploadsApi.getUpcoming(48),
        uploadsApi.getFailedUploads(),
        missedReplaysApi.getMissedReplays()
      ]);
      setPosts(postsData);
      setFailedUploads(failedData.failed_uploads || []);
      setMissedReplays(replaysData);
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
      setMessage({ type: 'error', text: err.message || 'Failed to schedule replay' });
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
      setMessage({ type: 'error', text: err.message || 'Failed to schedule replay' });
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
      setMessage({ type: 'error', text: err.message || 'Failed to schedule batch' });
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
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-white">Loading...</div>
      </div>
    );
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

      {/* Scheduled Uploads Section */}
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

      {/* Failed Uploads Section */}
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

      {/* Missed Replays Section */}
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
                  className={`bg-gray-900 border rounded-lg p-6 hover:border-gray-600 transition-colors ${
                    selectedReplays.has(replay.file_path) ? 'border-blue-500' : 'border-gray-700'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4 flex-1">
                      <button
                        onClick={() => toggleReplaySelection(replay.file_path)}
                        className="text-gray-400 hover:text-white transition-colors mt-1"
                      >
                        {selectedReplays.has(replay.file_path) ? (
                          <CheckSquare size={20} className="text-blue-500" />
                        ) : (
                          <Square size={20} />
                        )}
                      </button>
                      
                      <div className="flex-1">
                        <h3 className="text-white font-semibold mb-2">{replay.filename}</h3>
                        
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span>{formatFileSize(replay.file_size)} MB</span>
                          <span>•</span>
                          <span>Modified {formatTimeSince(replay.modified_time)}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 ml-4">
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
                        className="px-3 py-2 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white text-sm rounded-lg flex items-center gap-2 transition-colors"
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
    </div>
  );
};

export default UploadsPage;

