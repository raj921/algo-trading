import React, { useState, useEffect } from 'react';

function LiveFeed() {
  const [feedData, setFeedData] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  const symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'];

  useEffect(() => {
    const fetchLiveData = async () => {
      try {
        const promises = symbols.map(async (symbol) => {
          const response = await fetch(`http://localhost:8000/data/live/${symbol}`);
          if (response.ok) {
            return await response.json();
          }
          return null;
        });

        const results = await Promise.all(promises);
        const validResults = results.filter(result => result !== null);
        
        setFeedData(validResults);
        setIsConnected(true);
      } catch (error) {
        console.error('Error fetching live data:', error);
        setIsConnected(false);
      }
    };

    fetchLiveData();
    const interval = setInterval(fetchLiveData, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const getPriceChangeColor = (current, previous) => {
    if (current > previous) return 'text-green-600';
    if (current < previous) return 'text-red-600';
    return 'text-gray-600';
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">📡 Live Market Feed</h3>
        <div className={`flex items-center space-x-2 ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm">{isConnected ? 'Live' : 'Offline'}</span>
        </div>
      </div>

      <div className="space-y-3">
        {feedData.length > 0 ? (
          feedData.map((stock, index) => (
            <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="font-semibold text-lg">{stock.symbol}</div>
                <div className="text-sm text-gray-600">
                  Vol: {stock.volume.toLocaleString()}
                </div>
              </div>
              
              <div className="text-right">
                <div className="font-bold text-lg">
                  ${stock.price.toFixed(2)}
                </div>
                <div className="text-sm text-gray-600">
                  H: ${stock.high.toFixed(2)} | L: ${stock.low.toFixed(2)}
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-500 py-8">
            {isConnected ? 'Loading market data...' : 'Unable to connect to market data'}
          </div>
        )}
      </div>

      <div className="mt-4 text-xs text-gray-500 text-center">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
}

export default LiveFeed;