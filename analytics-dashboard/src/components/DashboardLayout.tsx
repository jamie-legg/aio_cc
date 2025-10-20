import React, { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TerminalHeader from './TerminalHeader';
import WatcherPanel from './WatcherPanel';
import LoadingScreen from './LoadingScreen';

const DashboardLayout: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-black text-white">
      <Sidebar />
      
      <div className="ml-60">
        <TerminalHeader />
        
        <main className="relative z-10">
          <Outlet />
        </main>
      </div>
      
      <WatcherPanel />
    </div>
  );
};

export default DashboardLayout;

