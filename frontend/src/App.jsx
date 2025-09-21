import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Trading from './components/Trading';
import Backtest from './components/Backtest';
import Portfolio from './components/Portfolio';
import LiveFeed from './components/LiveFeed';
import Navigation from './components/Navigation';

function App() {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Check backend connection
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setIsConnected(true);
        }
      } catch (error) {
        console.log('Backend not connected:', error);
        setIsConnected(false);
      }
    };

    checkConnection();
    const interval = setInterval(checkConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navigation isConnected={isConnected} />
        
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/trading" element={<Trading />} />
            <Route path="/backtest" element={<Backtest />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/live-feed" element={<LiveFeed />} />
          </Routes>
        </main>

        {!isConnected && (
          <div className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg">
            Backend Disconnected
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;
