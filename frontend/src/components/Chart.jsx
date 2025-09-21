import React, { useState, useEffect } from 'react';
import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

function Chart({ symbol }) {
  const [chartData, setChartData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setIsLoading(true);
        const response = await fetch('http://localhost:8000/data/historical', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            symbol: symbol,
            period: '30d',
            interval: '1d'
          })
        });

        if (response.ok) {
          const data = await response.json();
          setChartData(data);
        }
      } catch (error) {
        console.error('Error fetching chart data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchChartData();
  }, [symbol]);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse">
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!chartData || !chartData.data) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">
          No chart data available for {symbol}
        </div>
      </div>
    );
  }

  const data = chartData.data;

  // Compute SMA (20-period)
  const computeSMA = (data, period = 20) => {
    return data.map((d, i) => {
      if (i < period - 1) return { ...d, sma: null };
      const slice = data.slice(i - period + 1, i + 1);
      const sma = slice.reduce((sum, item) => sum + item.Close, 0) / period;
      return { ...d, sma };
    });
  };

  const processedData = computeSMA(data).map(d => ({
    date: new Date(d.Datetime).toLocaleDateString(),
    price: d.Close,
    sma: d.sma || null,
    volume: d.Volume
  })).filter(d => d.sma !== null); // Filter out initial nulls for SMA

  const minPrice = Math.min(...data.map(d => d.Low));
  const maxPrice = Math.max(...data.map(d => d.High));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold mb-4">{symbol} Price Chart (30 Days)</h3>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={processedData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis dataKey="date" stroke="#9ca3af" />
            <YAxis yAxisId="left" stroke="#9ca3af" domain={[minPrice, maxPrice]} />
            <YAxis yAxisId="right" orientation="right" stroke="#9ca3af" domain={['dataMin', 'dataMax']} />
            <Tooltip />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={2} name="Price" dot={false} />
            <Line yAxisId="left" type="monotone" dataKey="sma" stroke="#10b981" strokeWidth={2} name="SMA (20)" dot={false} />
            <Bar yAxisId="right" dataKey="volume" fill="#8884d8" name="Volume" barSize={20} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 text-sm text-gray-600">
        Data points: {chartData.data_points} |
        Current: ${data[data.length - 1].Close.toFixed(2)} |
        Range: ${minPrice.toFixed(2)} - ${maxPrice.toFixed(2)}
      </div>
    </div>
  );
}

export default Chart;