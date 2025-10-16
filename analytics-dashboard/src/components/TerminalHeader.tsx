import React, { useState, useEffect } from 'react';
import { Terminal, Wifi, WifiOff, RefreshCw, Settings } from 'lucide-react';

const TerminalHeader: React.FC = () => {
  const [isConnected, setIsConnected] = useState(true);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <header className="bg-terminal-card border-b-4 border-terminal-red px-6 py-4 sticky top-0 z-50 shadow-[0_4px_0px_#0080ff]">
      <div className="flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <Terminal size={24} className="text-terminal-red" />
          <span className="font-extrabold text-lg text-terminal-red uppercase tracking-wider">
            ANALYTICS_TERMINAL_v2.0
          </span>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            {isConnected ? (
              <Wifi size={16} className="text-terminal-red" />
            ) : (
              <WifiOff size={16} className="text-terminal-red" />
            )}
            <span className="text-xs font-bold uppercase tracking-wider text-terminal-red">
              {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
          
          <div className="font-mono text-sm text-gray-400 font-bold">
            {formatTime(currentTime)}
          </div>
          
          <div className="flex gap-3">
            <button className="brutalist-button flex items-center gap-2">
              <RefreshCw size={16} />
            </button>
            
            <button className="brutalist-button flex items-center gap-2">
              <Settings size={16} />
            </button>
          </div>
        </div>
      </div>
      
      <div className="h-1 bg-terminal-bg mt-3 rounded-sm overflow-hidden">
        <div className="h-full bg-gradient-to-r from-terminal-red via-terminal-blue to-terminal-red rounded-sm w-full" />
      </div>
    </header>
  );
};

export default TerminalHeader;