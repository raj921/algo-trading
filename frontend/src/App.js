import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Dashboard from './components/Dashboard'
import Trading from './components/Trading'
import Backtest from './components/Backtest'
import Portfolio from './components/Portfolio'
import LiveFeed from './components/LiveFeed'
import Chart from './components/Chart'
import { TrendingUp, BarChart3, PieChart, Activity, Zap } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  const navigation = [
    { name: 'Dashboard', href: '/', icon: TrendingUp, current: activeTab === 'dashboard' },
    { name: 'Live Trading', href: '/trading', icon: Activity, current: activeTab === 'trading' },
    { name: 'Backtest', href: '/backtest', icon: BarChart3, current: activeTab === 'backtest' },
    { name: 'Portfolio', href: '/portfolio', icon: PieChart, current: activeTab === 'portfolio' },
    { name: 'Live Feed', href: '/feed', icon: Zap, current: activeTab === 'feed' },
  ]

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Toaster position="top-right" />
        
        {/* Navigation */}
        <nav className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                      <TrendingUp className="w-5 h-5 text-white" />
                    </div>
                    <h1 className="ml-3 text-xl font-bold text-gray-900">AlgoTrader</h1>
                  </div>
                </div>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  {navigation.map((item) => {
                    const Icon = item.icon
                    return (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`${
                          item.current
                            ? 'border-blue-500 text-gray-900'
                            : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                        } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors`}
                        onClick={() => setActiveTab(item.name.toLowerCase().replace(' ', '-'))}
                      >
                        <Icon className="w-4 h-4 mr-2" />
                        {item.name}
                      </Link>
                    )
                  })}
                </div>
              </div>
              
              <div className="flex items-center">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span className="text-sm text-gray-600">Live</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {new Date().toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Mobile Navigation */}
        <div className="sm:hidden">
          <div className="pt-2 pb-3 space-y-1">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`${
                    item.current
                      ? 'bg-blue-50 border-blue-500 text-blue-700'
                      : 'border-transparent text-gray-500 hover:bg-gray-50 hover:border-gray-300 hover:text-gray-700'
                  } block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors`}
                  onClick={() => setActiveTab(item.name.toLowerCase().replace(' ', '-'))}
                >
                  <div className="flex items-center">
                    <Icon className="w-4 h-4 mr-3" />
                    {item.name}
                  </div>
                </Link>
              )
            })}
          </div>
        </div>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/trading" element={<Trading />} />
            <Route path="/backtest" element={<Backtest />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/feed" element={<LiveFeed />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200">
          <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">
                © 2024 AlgoTrader. Built for JarNox Internship.
              </div>
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>API Status: Connected</span>
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
