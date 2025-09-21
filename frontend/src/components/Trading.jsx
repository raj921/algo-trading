import React, { useState, useEffect } from 'react';
import Chart from './Chart';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';

function Trading() {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [selectedStrategy, setSelectedStrategy] = useState('sma_crossover');
  const [isTrading, setIsTrading] = useState(false);
  const [trades, setTrades] = useState([]);
  const [signals, setSignals] = useState([]);
  const [pnlData, setPnlData] = useState([]);
  const [livePrice, setLivePrice] = useState(null);

  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'];
  
  const strategies = [
    { id: 'sma_crossover', name: 'SMA Crossover', description: 'Moving average crossover strategy' },
    { id: 'rsi_momentum', name: 'RSI Momentum', description: 'RSI-based momentum strategy' },
    { id: 'bollinger_bands', name: 'Bollinger Bands', description: 'Mean reversion with Bollinger Bands' }
  ];

  useEffect(() => {
    const fetchLivePrice = async () => {
      try {
        const response = await fetch(`http://localhost:8000/data/live/${selectedSymbol}`);
        if (response.ok) {
          const data = await response.json();
          setLivePrice(data);
        }
      } catch (error) {
        console.error('Error fetching live price:', error);
      }
    };

    fetchLivePrice();
    const interval = setInterval(fetchLivePrice, 5000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const startTrading = async () => {
    setIsTrading(true);
    // Simulate trading activity with signals and P&L
    const basePrice = livePrice?.price || 150;
    const mockSignals = [
      { x: '2024-01-15', y: basePrice - 5, type: 'BUY', strategy: selectedStrategy },
      { x: '2024-01-20', y: basePrice, type: 'SELL', strategy: selectedStrategy },
      { x: '2024-02-01', y: basePrice + 2, type: 'BUY', strategy: selectedStrategy },
      { x: '2024-02-10', y: basePrice - 3, type: 'SELL', strategy: selectedStrategy }
    ];
    const mockTrades = mockSignals.map((signal, index) => ({
      id: index + 1,
      symbol: selectedSymbol,
      action: signal.type,
      price: signal.y,
      quantity: 100,
      timestamp: new Date(signal.x).toISOString()
    }));
    setSignals(mockSignals);
    setTrades(mockTrades);

    // Compute cumulative P&L
    const cumulativePnl = mockTrades.reduce((acc, trade, index) => {
      const pnl = index % 2 === 1 ? (trade.price - mockTrades[index - 1].price) * trade.quantity : 0;
      acc.push({ time: trade.timestamp, pnl: acc.length > 0 ? acc[acc.length - 1].pnl + pnl : pnl });
      return acc;
    }, []);
    setPnlData(cumulativePnl);
  };

  const stopTrading = () => {
    setIsTrading(false);
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Trading Interface
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Chart symbol={selectedSymbol} />
          </div>
          
          <div className="space-y-6">
            {/* Trading Controls */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Trading Controls</h3>
              
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
                
                {livePrice && (
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-sm text-gray-600">Current Price</div>
                    <div className="text-2xl font-bold text-blue-600">
                      ${livePrice.price.toFixed(2)}
                    </div>
                  </div>
                )}
                
                <div className="flex space-x-3">
                  {!isTrading ? (
                    <button
                      onClick={startTrading}
                      className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      Start Trading
                    </button>
                  ) : (
                    <button
                      onClick={stopTrading}
                      className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                    >
                      Stop Trading
                    </button>
                  )}
                </div>
              </div>
            </div>
            
            {/* Trade History */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Recent Trades</h3>
              
              <div className="space-y-2">
                {trades.length > 0 ? (
                  trades.map(trade => (
                    <div key={trade.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium">{trade.symbol}</div>
                        <div className="text-sm text-gray-600">
                          {new Date(trade.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`font-medium ${trade.action === 'BUY' ? 'text-green-600' : 'text-red-600'}`}>
                          {trade.action}
                        </div>
                        <div className="text-sm text-gray-600">
                          {trade.quantity} @ ${trade.price.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center text-gray-500 py-4">
                    No trades yet
                  </div>
                )}
              </div>
            </div>

            {/* P&L Chart */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Live P&L</h3>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={pnlData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis dataKey="time" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="pnl" stroke="#10b981" strokeWidth={2} name="Cumulative P&L" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Strategy Signals Chart */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold mb-4">Strategy Signals</h3>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                    <XAxis dataKey="x" type="category" name="Date" stroke="#9ca3af" />
                    <YAxis dataKey="y" type="number" name="Price" stroke="#9ca3af" />
                    <ZAxis type="number" range={[100]} />
                    <Tooltip />
                    <Legend />
                    <Scatter name="Signals" data={signals} fill="#8884d8">
                      {signals.map((entry, index) => (
                        <circle key={`signal-${index}`} cx={entry.x} cy={entry.y} r={4} fill={entry.type === 'BUY' ? '#10b981' : '#ef4444'} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Trading;