# 🚀 Algo Trading System - JarNox Internship

A comprehensive algorithmic trading system prototype built for the JarNox internship application. This system demonstrates live trading simulation, backtesting, and real-time portfolio management capabilities.

## 🎯 Project Overview

This project showcases a full-stack algorithmic trading system with the following core features:

### ✅ Core Requirements (Completed)
- **Data Feeds**: Live and historical data using yfinance API
- **Strategy Implementation**: SMA Crossover, RSI Momentum, Bollinger Bands
- **Backtesting Engine**: Comprehensive historical strategy testing
- **Paper Trading**: Real-time simulation with PnL tracking
- **Dashboard**: React-based visualization with live charts
- **Database**: PostgreSQL integration for trade logging

### 🌟 Bonus Features (Implemented)
- **Risk Management**: Stop loss, take profit, position sizing
- **WebSocket Support**: Live data streaming
- **Docker Deployment**: Complete containerization
- **Real-time Charts**: Interactive price charts with signals
- **Portfolio Management**: Position tracking and rebalancing
- **Performance Analytics**: Sharpe ratio, drawdown, win rate

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (PostgreSQL)   │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • Data Feeds    │    │ • Trades        │
│ • Trading UI    │    │ • Strategies    │    │ • Positions     │
│ • Charts        │    │ • Backtesting   │    │ • Performance   │
│ • Portfolio     │    │ • Paper Trading │    │ • Market Data   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Option 1: Docker (Recommended)
```bash
# clone the repository
git clone <repository-url>
cd algo-trading-prototype

# start all services
docker-compose up -d

# access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development
```bash
# backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# frontend setup (in new terminal)
cd frontend
npm install
npm run dev
```

## 📊 Features Overview

### 1. Data Feeds
- **Live Data**: Real-time price feeds using yfinance
- **Historical Data**: 1-minute to daily intervals
- **WebSocket Support**: Live streaming updates
- **Multiple Symbols**: Stocks and cryptocurrencies

### 2. Trading Strategies
- **SMA Crossover**: Simple moving average crossover signals
- **RSI Momentum**: Relative Strength Index momentum strategy
- **Bollinger Bands**: Mean reversion using volatility bands

### 3. Backtesting Engine
- **Historical Testing**: Test strategies on past data
- **Performance Metrics**: Sharpe ratio, max drawdown, win rate
- **Trade Analysis**: Detailed trade-by-trade breakdown
- **Strategy Comparison**: Compare multiple strategies

### 4. Paper Trading
- **Live Simulation**: Real-time strategy execution
- **PnL Tracking**: Profit/loss monitoring
- **Risk Management**: Stop loss and take profit
- **Position Sizing**: Configurable position limits

### 5. Dashboard & Visualization
- **Live Charts**: Real-time price charts with signals
- **Portfolio Overview**: Current positions and performance
- **Performance Analytics**: Historical performance metrics
- **Risk Monitoring**: Real-time risk metrics

## 🔧 API Endpoints

### Data Endpoints
- `GET /data/live/{symbol}` - Get live price for symbol
- `POST /data/historical` - Get historical data
- `GET /data/symbols` - List available symbols

### Strategy Endpoints
- `POST /strategies/sma-crossover` - Create SMA strategy
- `POST /strategies/rsi-momentum` - Create RSI strategy
- `POST /strategies/bollinger-bands` - Create Bollinger strategy

### Backtesting Endpoints
- `POST /backtest/run` - Run strategy backtest
- `GET /backtest/results` - Get backtest results
- `GET /backtest/compare` - Compare strategies

### Portfolio Endpoints
- `GET /portfolio/summary` - Get portfolio overview
- `POST /portfolio/trade` - Execute manual trade
- `GET /portfolio/performance` - Get performance metrics

### Paper Trading Endpoints
- `POST /paper-trading/start` - Start paper trading
- `POST /paper-trading/stop` - Stop paper trading
- `GET /paper-trading/status` - Get trading status

## 🎨 Frontend Components

### Dashboard
- Portfolio overview with key metrics
- Live market data grid
- Performance charts
- System status indicators

### Trading Interface
- Strategy selection and configuration
- Risk management controls
- Live trading status
- Performance monitoring

### Backtesting
- Strategy configuration
- Historical data selection
- Results visualization
- Strategy comparison

### Portfolio Management
- Position overview
- Trade execution
- Performance analytics
- Risk metrics

### Live Feed
- Real-time price updates
- WebSocket connection status
- Market summary
- Symbol selection

## 🗄️ Database Schema

### Core Tables
- **Symbols**: Market symbols and metadata
- **Trades**: Executed trades with details
- **Positions**: Current portfolio positions
- **Portfolio Snapshots**: Historical portfolio values
- **Strategies**: Trading strategy definitions
- **Signals**: Generated trading signals
- **Market Data**: Historical price data

## 🔒 Risk Management

### Position-Level Risk
- Maximum position size limits
- Stop loss orders
- Take profit targets
- Position sizing controls

### Portfolio-Level Risk
- Maximum drawdown limits
- Portfolio diversification
- Correlation monitoring
- Exposure limits

## 📈 Performance Metrics

### Return Metrics
- Total return percentage
- Annualized return
- Risk-adjusted returns

### Risk Metrics
- Maximum drawdown
- Value at Risk (VaR)
- Sharpe ratio
- Sortino ratio
- Calmar ratio

### Trade Metrics
- Win rate
- Average trade return
- Profit factor
- Trade frequency

## 🚀 Deployment

### Docker Deployment
The system is fully containerized with Docker Compose:

```yaml
services:
  - postgres: Database
  - redis: Caching and task queue
  - backend: FastAPI application
  - frontend: React application
  - nginx: Reverse proxy
  - celery-worker: Background tasks
  - celery-beat: Scheduled tasks
```

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/trading_system
REDIS_URL=redis://localhost:6379
INITIAL_CAPITAL=10000
COMMISSION_RATE=0.001
MAX_POSITION_SIZE=0.2
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📝 Development Approach

### Technology Stack
- **Backend**: Python, FastAPI, SQLAlchemy, Peewee
- **Frontend**: React, Vite, Recharts, Tailwind CSS
- **Database**: PostgreSQL, Redis
- **Data**: yfinance, pandas, numpy
- **Deployment**: Docker, Docker Compose, Nginx

### Development Principles
- **Modular Design**: Separated concerns with clear interfaces
- **Real-time Updates**: WebSocket integration for live data
- **Risk-First**: Built-in risk management at every level
- **Performance**: Optimized for speed and scalability
- **User Experience**: Intuitive dashboard and controls

## 🎓 Challenges & Learnings

### Technical Challenges
1. **Real-time Data Handling**: Managing live data feeds and WebSocket connections
2. **Strategy Implementation**: Ensuring accurate signal generation and execution
3. **Risk Management**: Implementing comprehensive risk controls
4. **Performance Optimization**: Handling large datasets efficiently

### Key Learnings
1. **Market Data Complexity**: Understanding different data sources and formats
2. **Strategy Backtesting**: Importance of proper historical testing
3. **Risk Management**: Critical role of risk controls in trading systems
4. **User Interface**: Balancing functionality with usability

### Future Enhancements
- Machine learning price prediction models
- Advanced order types (limit, stop, trailing)
- Multi-asset portfolio optimization
- Real broker API integration
- Mobile application

## 📞 Contact

Built for the JarNox Algo Trading Internship application.

**Submission Email**: shaktijarnox@outlook.com

---


