import React, { useState, useEffect } from 'react';
import Chart from './Chart';
import Portfolio from './Portfolio';
import LiveFeed from './LiveFeed';

function Dashboard() {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [searchTerm, setSearchTerm] = useState('');
  const [livePrice, setLivePrice] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'];
  const filteredSymbols = symbols.filter(symbol =>
    symbol.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
    setIsLoading(false);

    const interval = setInterval(fetchLivePrice, 5000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">
          Trading Dashboard
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">Live Price Chart</h2>
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search symbol..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-32"
                />
                {searchTerm && (
                  <ul className="absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-md shadow-lg max-h-40 overflow-auto z-10">
                    {filteredSymbols.map(symbol => (
                      <li key={symbol}>
                        <button
                          onClick={() => {
                            setSelectedSymbol(symbol);
                            setSearchTerm('');
                          }}
                          className="w-full text-left px-3 py-2 hover:bg-gray-100"
                        >
                          {symbol}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
            
            {livePrice && (
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-blue-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Current Price</div>
                  <div className="text-lg font-bold text-blue-600">
                    ${livePrice.price.toFixed(2)}
                  </div>
                </div>
                <div className="bg-green-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">High</div>
                  <div className="text-lg font-bold text-green-600">
                    ${livePrice.high.toFixed(2)}
                  </div>
                </div>
                <div className="bg-red-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Low</div>
                  <div className="text-lg font-bold text-red-600">
                    ${livePrice.low.toFixed(2)}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <div className="text-sm text-gray-600">Volume</div>
                  <div className="text-lg font-bold text-gray-600">
                    {livePrice.volume.toLocaleString()}
                  </div>
                </div>
              </div>
            )}
            
            <Chart symbol={selectedSymbol} />
          </div>
          
          <div className="space-y-6">
            <Portfolio />
            <LiveFeed />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;