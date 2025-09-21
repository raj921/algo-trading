import React, { useState, useEffect } from 'react';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  ComposedChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

function Backtest() {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [selectedStrategy, setSelectedStrategy] = useState('sma_crossover');
  const [period, setPeriod] = useState('1y');
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);

  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'];
  
  const strategies = [
    { id: 'sma_crossover', name: 'SMA Crossover', description: 'Moving average crossover strategy' },
    { id: 'rsi_momentum', name: 'RSI Momentum', description: 'RSI-based momentum strategy' },
    { id: 'bollinger_bands', name: 'Bollinger Bands', description: 'Mean reversion with Bollinger Bands' }
  ];

  const periods = [
    { id: '1m', name: '1 Month' },
    { id: '3m', name: '3 Months' },
    { id: '6m', name: '6 Months' },
    { id: '1y', name: '1 Year' },
    { id: '2y', name: '2 Years' },
    { id: '5y', name: '5 Years' }
  ];

  const runBacktest = async () => {
    setIsRunning(true);
    
    // Simulate backtest results
    setTimeout(() => {
      const trades = [
        { date: '2024-01-15', action: 'BUY', price: 150.00, quantity: 100, pnl: 0 },
        { date: '2024-01-20', action: 'SELL', price: 155.00, quantity: 100, pnl: 500 },
        { date: '2024-02-01', action: 'BUY', price: 152.00, quantity: 100, pnl: 0 },
        { date: '2024-02-10', action: 'SELL', price: 148.00, quantity: 100, pnl: -400 },
        { date: '2024-03-01', action: 'BUY', price: 145.00, quantity: 100, pnl: 0 },
        { date: '2024-03-15', action: 'SELL', price: 160.00, quantity: 100, pnl: 1500 },
        // More trades for curve
      ];

      let equity = 100000;
      let maxEquity = 100000;
      const equityData = [];
      const drawdownData = [];
      trades.forEach(trade => {
        equity += trade.pnl;
        maxEquity = Math.max(maxEquity, equity);
        const drawdown = ((equity - maxEquity) / maxEquity) * 100;
        equityData.push({ date: trade.date, equity });
        drawdownData.push({ date: trade.date, drawdown });
      });

      const mockResults = {
        symbol: selectedSymbol,
        strategy: selectedStrategy,
        period: period,
        startDate: '2024-01-01',
        endDate: '2024-12-31',
        initialCapital: 100000,
        finalCapital: equity,
        totalReturn: equity - 100000,
        totalReturnPercentage: ((equity - 100000) / 100000) * 100,
        sharpeRatio: 1.45,
        maxDrawdown: Math.min(...drawdownData.map(d => d.drawdown)),
        totalTrades: trades.length,
        winningTrades: trades.filter(t => t.pnl > 0).length,
        losingTrades: trades.filter(t => t.pnl < 0).length,
        winRate: (trades.filter(t => t.pnl > 0).length / trades.length) * 100,
        averageWin: trades.filter(t => t.pnl > 0).reduce((sum, t) => sum + t.pnl, 0) / trades.filter(t => t.pnl > 0).length || 0,
        averageLoss: trades.filter(t => t.pnl < 0).reduce((sum, t) => sum + t.pnl, 0) / trades.filter(t => t.pnl < 0).length || 0,
        profitFactor: Math.abs(trades.filter(t => t.pnl > 0).reduce((sum, t) => sum + t.pnl, 0) / trades.filter(t => t.pnl < 0).reduce((sum, t) => sum + t.pnl, 0)) || 0,
        trades: trades,
        equityData,
        drawdownData,
        tradeMarkers: trades.map(t => ({ x: t.date, y: t.price, type: t.action, pnl: t.pnl }))
      };
      setResults(mockResults);
      setIsRunning(false);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          📈 Strategy Backtesting
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            {/* Backtest Configuration */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Backtest Configuration</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Symbol
                  </label>
                  <select
                    value={selectedSymbol}
                    onChange={(e) => setSelectedSymbol(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {symbols.map(symbol => (
                      <option key={symbol} value={symbol}>{symbol}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Strategy
                  </label>
                  <select
                    value={selectedStrategy}
                    onChange={(e) => setSelectedStrategy(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {strategies.map(strategy => (
                      <option key={strategy.id} value={strategy.id}>
                        {strategy.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-sm text-gray-600 mt-1">
                    {strategies.find(s => s.id === selectedStrategy)?.description}
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Period
                  </label>
                  <select
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {periods.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                
                <button
                  onClick={runBacktest}
                  disabled={isRunning}
                  className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isRunning ? 'Running Backtest...' : 'Run Backtest'}
                </button>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-2">
            {results ? (
              <div className="space-y-6">
                {/* Performance Summary */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4">Performance Summary</h3>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">Total Return</div>
                      <div className="text-2xl font-bold text-green-600">
                        +{results.totalReturnPercentage.toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">
                        ${results.totalReturn.toLocaleString()}
                      </div>
                    </div>
                    
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">Sharpe Ratio</div>
                      <div className="text-2xl font-bold text-blue-600">
                        {results.sharpeRatio}
                      </div>
                    </div>
                    
                    <div className="bg-red-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">Max Drawdown</div>
                      <div className="text-2xl font-bold text-red-600">
                        {results.maxDrawdown.toFixed(1)}%
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <div className="text-sm text-gray-600">Win Rate</div>
                      <div className="text-2xl font-bold text-gray-600">
                        {results.winRate.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Trade Statistics */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4">Trade Statistics</h3>
                  
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{results.totalTrades}</div>
                      <div className="text-sm text-gray-600">Total Trades</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{results.winningTrades}</div>
                      <div className="text-sm text-gray-600">Winning Trades</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{results.losingTrades}</div>
                      <div className="text-sm text-gray-600">Losing Trades</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">${results.averageWin}</div>
                      <div className="text-sm text-gray-600">Avg Win</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">${results.averageLoss}</div>
                      <div className="text-sm text-gray-600">Avg Loss</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{results.profitFactor}</div>
                      <div className="text-sm text-gray-600">Profit Factor</div>
                    </div>
                  </div>
                </div>

                {/* Equity Curve Chart */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={results.equityData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                        <XAxis dataKey="date" stroke="#9ca3af" />
                        <YAxis stroke="#9ca3af" />
                        <Tooltip />
                        <Legend />
                        <Area type="monotone" dataKey="equity" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Drawdown and Trade Markers Chart */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4">Price Chart with Trade Markers & Drawdown</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={results.equityData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                        <XAxis dataKey="date" stroke="#9ca3af" />
                        <YAxis yAxisId="left" stroke="#9ca3af" />
                        <YAxis yAxisId="right" orientation="right" stroke="#ef4444" />
                        <Tooltip />
                        <Legend />
                        <Line yAxisId="right" type="monotone" data={results.drawdownData} dataKey="drawdown" stroke="#ef4444" name="Drawdown (%)" />
                        <Scatter yAxisId="left" data={results.tradeMarkers} fill="#8884d8">
                          {results.tradeMarkers.map((entry, index) => (
                            <circle key={`marker-${index}`} cx={entry.x} cy={entry.y} r={4} fill={entry.type === 'BUY' ? '#10b981' : '#ef4444'} />
                          ))}
                        </Scatter>
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                
                {/* Recent Trades */}
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-semibold mb-4">Recent Trades</h3>
                  
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-2">Date</th>
                          <th className="text-left py-2">Action</th>
                          <th className="text-left py-2">Price</th>
                          <th className="text-left py-2">Quantity</th>
                          <th className="text-left py-2">P&L</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.trades.slice(0, 10).map((trade, index) => (
                          <tr key={index} className="border-b">
                            <td className="py-2">{trade.date}</td>
                            <td className={`py-2 font-medium ${trade.action === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                              {trade.action}
                            </td>
                            <td className="py-2">${trade.price.toFixed(2)}</td>
                            <td className="py-2">{trade.quantity}</td>
                            <td className={`py-2 font-medium ${trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <div className="text-gray-500 text-lg">
                  {isRunning ? 'Running backtest...' : 'Configure and run a backtest to see results'}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Backtest;