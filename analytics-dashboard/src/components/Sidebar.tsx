import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { BarChart3, Upload, Sparkles, Webhook, Settings, LogOut, User, BookOpen } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Sidebar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  const navItems = [
    {
      path: '/dashboard',
      icon: <BarChart3 size={20} />,
      label: 'Analytics',
      end: true
    },
    {
      path: '/dashboard/uploads',
      icon: <Upload size={20} />,
      label: 'Uploads'
    },
    {
      path: '/dashboard/ai-config',
      icon: <Sparkles size={20} />,
      label: 'AI Config'
    },
    {
      path: '/dashboard/integrations',
      icon: <Webhook size={20} />,
      label: 'Integrations'
    },
    {
      path: '/dashboard/docs',
      icon: <BookOpen size={20} />,
      label: 'Documentation'
    },
    {
      path: '/dashboard/settings',
      icon: <Settings size={20} />,
      label: 'Settings'
    }
  ];

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-gray-900 border-r border-gray-700 z-40">
      <div className="p-6">
        <h1 className="text-xl font-bold text-white">AIOCC</h1>
        <p className="text-xs text-gray-400 mt-1">Content Creation</p>
      </div>
      
      <nav className="px-3">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors duration-200 ${
                isActive
                  ? 'bg-gray-800 text-white border-l-4 border-blue-500'
                  : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
              }`
            }
          >
            {item.icon}
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>
      
      <div className="absolute bottom-0 left-0 right-0 border-t border-gray-700">
        {/* User Info */}
        {user && (
          <div className="p-4 border-b border-gray-700">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center">
                <User size={20} className="text-gray-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{user.username}</p>
                <p className="text-xs text-gray-500 truncate">{user.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded-lg transition-colors"
            >
              <LogOut size={16} />
              <span className="text-sm font-medium">Logout</span>
            </button>
          </div>
        )}
        
        {/* Version */}
        <div className="p-4">
          <p className="text-xs text-gray-500 text-center">
            v1.0.0
          </p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

