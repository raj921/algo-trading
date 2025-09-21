import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navigation({ isConnected }) {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/trading', label: 'Trading', icon: '💰' },
    { path: '/backtest', label: 'Backtest', icon: '📈' },
    { path: '/portfolio', label: 'Portfolio', icon: '💼' },
    { path: '/live-feed', label: 'Live Feed', icon: '📡' },
  ];

  return (
    <nav className="bg-white shadow-lg border-b">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <Link to="/" className="text-xl font-bold text-blue-600">
              Algo Trading System
            </Link>
            
            <div className="hidden md:flex space-x-6">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    location.pathname === item.path
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:text-blue-600 hover:bg-gray-100'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-4">
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navigation;
