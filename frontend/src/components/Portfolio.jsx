import React, { useState, useEffect } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip
} from 'recharts';

function Portfolio() {
  const [portfolio, setPortfolio] = useState({
    totalValue: 100000,
    cash: 50000,
    positions: [
      { symbol: 'AAPL', shares: 100, avgPrice: 150.00, currentPrice: 245.29 },
      { symbol: 'MSFT', shares: 50, avgPrice: 300.00, currentPrice: 412.50 },
      { symbol: 'GOOGL', shares: 25, avgPrice: 2500.00, currentPrice: 2780.00 },
    ]
  });

  const calculatePnL = (shares, avgPrice, currentPrice) => {
    return (currentPrice - avgPrice) * shares;
  };

  const calculateTotalPnL = () => {
    return portfolio.positions.reduce((total, position) => {
      return total + calculatePnL(position.shares, position.avgPrice, position.currentPrice);
    }, 0);
  };

  const totalPnL = calculateTotalPnL();
  const totalPnLPercentage = (totalPnL / portfolio.totalValue) * 100;

  // Compute allocation for pie chart
  const allocationData = portfolio.positions.map(position => {
    const currentValue = position.shares * position.currentPrice;
    return {
      name: position.symbol,
      value: currentValue,
      fill: ['#3b82f6', '#10b981', '#f59e0b'][portfolio.positions.indexOf(position) % 3]
    };
  });

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">💼 Portfolio Overview</h3>
      
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600">Total Value</div>
            <div className="text-lg font-bold">
              ${portfolio.totalValue.toLocaleString()}
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="text-sm text-gray-600">Cash</div>
            <div className="text-lg font-bold">
              ${portfolio.cash.toLocaleString()}
            </div>
          </div>
        </div>
        
        <div className={`p-3 rounded-lg ${totalPnL >= 0 ? 'bg-green-50' : 'bg-red-50'}`}>
          <div className="text-sm text-gray-600">Total P&L</div>
          <div className={`text-lg font-bold ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)} ({totalPnLPercentage >= 0 ? '+' : ''}{totalPnLPercentage.toFixed(2)}%)
          </div>
        </div>

        {/* Allocation Pie Chart */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="font-medium mb-2">Portfolio Allocation</h4>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                  nameKey="name"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        <div>
          <h4 className="font-medium mb-2">Positions</h4>
          <div className="space-y-2">
            {portfolio.positions.map((position, index) => {
              const pnl = calculatePnL(position.shares, position.avgPrice, position.currentPrice);
              const pnlPercentage = ((position.currentPrice - position.avgPrice) / position.avgPrice) * 100;
              const currentValue = position.shares * position.currentPrice;
              
              return (
                <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                  <div>
                    <div className="font-medium">{position.symbol}</div>
                    <div className="text-sm text-gray-600">
                      {position.shares} shares @ ${position.avgPrice.toFixed(2)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-medium">${currentValue.toFixed(2)}</div>
                    <div className={`text-sm ${pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)} ({pnlPercentage >= 0 ? '+' : ''}{pnlPercentage.toFixed(1)}%)
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Portfolio;