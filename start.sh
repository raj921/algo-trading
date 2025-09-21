#!/bin/bash

echo "🚀 Starting Algo Trading System..."
echo "=================================="

# check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

echo "📦 Building and starting services..."
docker-compose up -d --build

echo "⏳ Waiting for services to start..."
sleep 10

echo "🧪 Running system tests..."
python test_system.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 System started successfully!"
    echo ""
    echo "🌐 Frontend Dashboard: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo ""
    echo "📊 Features Available:"
    echo "   • Live market data feeds"
    echo "   • Multiple trading strategies"
    echo "   • Backtesting engine"
    echo "   • Paper trading simulation"
    echo "   • Portfolio management"
    echo "   • Real-time dashboard"
    echo ""
    echo "🛑 To stop the system: docker-compose down"
    echo "📋 To view logs: docker-compose logs -f"
else
    echo "❌ System startup failed. Check the logs:"
    echo "   docker-compose logs"
    exit 1
fi
