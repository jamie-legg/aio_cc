import React, { useState, useEffect, useRef } from 'react';
import {
  Eye,
  Minimize2,
  X,
  Search,
  Trash2,
  Circle,
  Activity,
  Folder,
  Video,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { watcherService, WatcherEvent, OBSStatus } from '../services/watcherService';
import ActivityLogItem from './ActivityLogItem';

const WatcherPanel: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [events, setEvents] = useState<WatcherEvent[]>([]);
  const [filteredEvents, setFilteredEvents] = useState<WatcherEvent[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [watcherStatus, setWatcherStatus] = useState<'idle' | 'watching' | 'processing'>('idle');
  const [activeCount, setActiveCount] = useState(0);
  const [obsStatus, setObsStatus] = useState<OBSStatus | null>(null);
  const logContainerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Load panel state from localStorage
  useEffect(() => {
    const savedState = localStorage.getItem('watcherPanelExpanded');
    if (savedState !== null) {
      setIsExpanded(JSON.parse(savedState));
    }
  }, []);

  // Save panel state to localStorage
  useEffect(() => {
    localStorage.setItem('watcherPanelExpanded', JSON.stringify(isExpanded));
  }, [isExpanded]);

  // Initialize watcher service
  useEffect(() => {
    // Connect to SSE
    watcherService.connect();

    // Load history
    watcherService.getHistory().then(history => {
      setEvents(history);
      setFilteredEvents(history);
    }).catch(err => {
      console.error('Failed to load history:', err);
    });

    // Load initial status
    watcherService.getStatus().then(status => {
      setWatcherStatus(status.status);
    }).catch(err => {
      console.error('Failed to load status:', err);
    });

    // Load OBS status
    watcherService.getOBSStatus().then(status => {
      setObsStatus(status);
    }).catch(err => {
      console.error('Failed to load OBS status:', err);
    });

    // Subscribe to events
    const unsubscribeEvent = watcherService.onEvent((event) => {
      setEvents(prev => {
        const newEvents = [...prev, event];
        // Keep only last 100 events
        if (newEvents.length > 100) {
          newEvents.shift();
        }
        return newEvents;
      });

      // Update active count for processing events
      if (event.status === 'processing') {
        setActiveCount(prev => prev + 1);
      } else if (event.status === 'success' || event.status === 'error') {
        setActiveCount(prev => Math.max(0, prev - 1));
      }
    });

    // Subscribe to status changes
    const unsubscribeStatus = watcherService.onStatusChange((connected) => {
      setIsConnected(connected);
    });

    // Listen for refresh events from header
    const handleRefresh = () => {
      watcherService.getHistory().then(history => {
        setEvents(history);
        setFilteredEvents(history);
      }).catch(err => {
        console.error('Failed to reload history:', err);
      });
      
      watcherService.getStatus().then(status => {
        setWatcherStatus(status.status);
      }).catch(err => {
        console.error('Failed to reload status:', err);
      });
      
      watcherService.getOBSStatus().then(status => {
        setObsStatus(status);
      }).catch(err => {
        console.error('Failed to reload OBS status:', err);
      });
    };
    
    window.addEventListener('dashboard-refresh', handleRefresh);

    // Cleanup on unmount
    return () => {
      unsubscribeEvent();
      unsubscribeStatus();
      watcherService.disconnect();
      window.removeEventListener('dashboard-refresh', handleRefresh);
    };
  }, []);

  // Filter events based on search query
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredEvents(events);
      return;
    }

    const query = searchQuery.toLowerCase();
    const filtered = events.filter(event =>
      event.filename.toLowerCase().includes(query) ||
      event.message.toLowerCase().includes(query) ||
      event.platform?.toLowerCase().includes(query) ||
      event.status.toLowerCase().includes(query)
    );
    setFilteredEvents(filtered);
  }, [searchQuery, events]);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [filteredEvents, autoScroll]);

  // Handle manual scroll to detect if user scrolled up
  const handleScroll = () => {
    if (logContainerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = logContainerRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      setAutoScroll(isAtBottom);
    }
  };

  // Clear history
  const handleClearHistory = async () => {
    if (confirm('Clear all event history?')) {
      try {
        await watcherService.clearHistory();
        setEvents([]);
        setFilteredEvents([]);
        setActiveCount(0);
      } catch (err) {
        console.error('Failed to clear history:', err);
      }
    }
  };

  // Get status indicator color
  const getStatusColor = () => {
    if (!isConnected) return 'bg-gray-500';
    switch (watcherStatus) {
      case 'watching':
        return 'bg-green-500';
      case 'processing':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <>
      {/* FAB Button (Collapsed State) */}
      <AnimatePresence>
        {!isExpanded && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={() => setIsExpanded(true)}
            className="fixed bottom-6 right-6 w-14 h-14 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-full shadow-lg flex items-center justify-center transition-colors z-50"
            aria-label="Open watcher activity"
          >
            <Eye size={24} className="text-white" />
            
            {/* Badge for active count */}
            {activeCount > 0 && (
              <span className="absolute -top-1 -right-1 w-6 h-6 bg-blue-500 text-white text-xs font-bold rounded-full flex items-center justify-center border-2 border-gray-900">
                {activeCount}
              </span>
            )}

            {/* Connection indicator */}
            <span className={`absolute bottom-0 right-0 w-3 h-3 ${getStatusColor()} rounded-full border-2 border-gray-900`} />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Expanded Panel */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ y: '100%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: '100%', opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className="fixed bottom-0 right-6 w-[400px] h-[600px] bg-gray-900 border border-gray-700 rounded-t-xl shadow-2xl flex flex-col z-50"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-700">
              <div className="flex items-center gap-3">
                <Activity size={20} className="text-white" />
                <h3 className="text-white font-semibold">Content Watcher</h3>
                
                {/* Status Indicator */}
                <div className="flex items-center gap-1.5">
                  <Circle size={8} className={`${getStatusColor()} fill-current`} />
                  <span className="text-xs text-gray-400 capitalize">{watcherStatus}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsExpanded(false)}
                  className="p-1.5 hover:bg-gray-800 rounded transition-colors"
                  aria-label="Minimize"
                >
                  <Minimize2 size={16} className="text-gray-400" />
                </button>
                <button
                  onClick={() => setIsExpanded(false)}
                  className="p-1.5 hover:bg-gray-800 rounded transition-colors"
                  aria-label="Close"
                >
                  <X size={16} className="text-gray-400" />
                </button>
              </div>
            </div>

            {/* Watch Directory Info */}
            {obsStatus && obsStatus.replay_buffer_path && (
              <div className="px-4 py-3 bg-gray-800/50 border-b border-gray-700">
                <div className="flex items-start gap-2">
                  <Folder size={16} className="text-blue-400 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs font-medium text-gray-400">Watching</span>
                      {obsStatus.obs_running && (
                        <div className="flex items-center gap-1 px-2 py-0.5 bg-green-500/20 border border-green-500/30 rounded-full">
                          <Video size={10} className="text-green-400" />
                          <span className="text-xs text-green-400">OBS Auto-Detected</span>
                        </div>
                      )}
                    </div>
                    <p className="text-xs text-white font-mono truncate" title={obsStatus.replay_buffer_path}>
                      {obsStatus.replay_buffer_path}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Search and Actions */}
            <div className="p-3 border-b border-gray-700">
              <div className="flex items-center gap-2">
                <div className="flex-1 relative">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search events..."
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-gray-600"
                  />
                </div>
                <button
                  onClick={handleClearHistory}
                  className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                  title="Clear history"
                >
                  <Trash2 size={16} className="text-gray-400" />
                </button>
              </div>
            </div>

            {/* Event Log */}
            <div
              ref={logContainerRef}
              onScroll={handleScroll}
              className="flex-1 overflow-y-auto"
            >
              {filteredEvents.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-500 p-6 text-center">
                  <Eye size={48} className="mb-3 opacity-50" />
                  <p className="text-sm">
                    {searchQuery ? 'No events match your search' : 'No activity yet'}
                  </p>
                  <p className="text-xs mt-1">
                    {!searchQuery && 'Drop a video file to see activity'}
                  </p>
                </div>
              ) : (
                <div>
                  {filteredEvents.map((event, index) => (
                    <ActivityLogItem
                      key={`${event.timestamp}-${index}`}
                      event={event}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-2 border-t border-gray-700 text-center">
              <div className="flex items-center justify-between px-2">
                <span className="text-xs text-gray-500">
                  {filteredEvents.length} {filteredEvents.length === 1 ? 'event' : 'events'}
                </span>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                  <span className="text-xs text-gray-500">
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default WatcherPanel;

