from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
import uvicorn
from datetime import datetime
import pandas as pd

# import our modules
from data.data_feed import DataFeed, MockDataFeed
from data.indicators import TechnicalIndicators
from strategies.sma_crossover import SMACrossoverStrategy
from strategies.rsi_momentum import RSIMomentumStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from trading.backtest import BacktestEngine
from trading.paper_trading import PaperTradingEngine
from trading.portfolio import Portfolio
from database.models import init_database, save_trade, save_market_data, save_signal

# initialize fastapi app
app = FastAPI(title="Algo Trading System", version="1.0.0")

# add cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# global variables
data_feed = None
backtest_engine = BacktestEngine()
paper_trading_engine = None
portfolio = Portfolio()

# pydantic models
class SymbolRequest(BaseModel):
    symbol: str
    period: str = "1y"
    interval: str = "1d"

class BacktestRequest(BaseModel):
    symbol: str
    strategy: str
    period: str = "1y"
    interval: str = "1d"
    initial_capital: float = 10000
    position_size: float = 0.1

class StrategyRequest(BaseModel):
    symbol: str
    strategy_name: str
    parameters: Dict

class TradeRequest(BaseModel):
    symbol: str
    trade_type: str
    quantity: float
    price: float

@app.on_event("startup")
async def startup_event():
    print("initializing algo trading system...")
    init_database()
    
    global data_feed
    data_feed = DataFeed()
    
    global paper_trading_engine
    paper_trading_engine = PaperTradingEngine()
    
    print("system initialization completed")

@app.get("/")
async def root():
    return {
        "message": "algo trading system api",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_feed": "connected" if data_feed else "disconnected"
    }

# data endpoints
@app.post("/data/historical")
async def get_historical_data(request: SymbolRequest):
    try:
        data = data_feed.get_historical_data(
            request.symbol, 
            request.period, 
            request.interval
        )
        
        if data is None:
            raise HTTPException(status_code=404, detail="no data found for symbol")
        
        # save to database
        for _, row in data.iterrows():
            save_market_data(
                request.symbol,
                row['Datetime'],
                row['Open'],
                row['High'],
                row['Low'],
                row['Close'],
                row.get('Volume', 0)
            )
        
        return {
            "symbol": request.symbol,
            "data_points": len(data),
            "data": data.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/live/{symbol}")
async def get_live_price(symbol: str):
    try:
        live_data = data_feed.get_live_price(symbol)
        if live_data is None:
            raise HTTPException(status_code=404, detail="could not fetch live price")
        
        return live_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/symbols")
async def get_available_symbols():
    return {
        "symbols": [
            "AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX",
            "BTC-USD", "ETH-USD", "ADA-USD", "DOT-USD"
        ]
    }

# strategy endpoints
@app.post("/strategies/sma-crossover")
async def create_sma_strategy(request: StrategyRequest):
    try:
        strategy = SMACrossoverStrategy(
            fast_period=request.parameters.get('fast_period', 20),
            slow_period=request.parameters.get('slow_period', 50),
            symbol=request.symbol
        )
        
        return {
            "strategy": "SMA Crossover",
            "symbol": request.symbol,
            "parameters": request.parameters,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/strategies/rsi-momentum")
async def create_rsi_strategy(request: StrategyRequest):
    try:
        strategy = RSIMomentumStrategy(
            rsi_period=request.parameters.get('rsi_period', 14),
            oversold=request.parameters.get('oversold', 30),
            overbought=request.parameters.get('overbought', 70),
            symbol=request.symbol
        )
        
        return {
            "strategy": "RSI Momentum",
            "symbol": request.symbol,
            "parameters": request.parameters,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/strategies/bollinger-bands")
async def create_bollinger_strategy(request: StrategyRequest):
    try:
        strategy = BollingerBandsStrategy(
            period=request.parameters.get('period', 20),
            std_dev=request.parameters.get('std_dev', 2),
            symbol=request.symbol
        )
        
        return {
            "strategy": "Bollinger Bands",
            "symbol": request.symbol,
            "parameters": request.parameters,
            "status": "created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# backtesting endpoints
@app.post("/backtest/run")
async def run_backtest(request: BacktestRequest):
    try:
        # get historical data
        data = data_feed.get_historical_data(
            request.symbol,
            request.period,
            request.interval
        )
        
        if data is None:
            raise HTTPException(status_code=404, detail="no historical data available")
        
        # create strategy
        if request.strategy == "sma_crossover":
            strategy = SMACrossoverStrategy(symbol=request.symbol)
        elif request.strategy == "rsi_momentum":
            strategy = RSIMomentumStrategy(symbol=request.symbol)
        elif request.strategy == "bollinger_bands":
            strategy = BollingerBandsStrategy(symbol=request.symbol)
        else:
            raise HTTPException(status_code=400, detail="unsupported strategy")
        
        # run backtest
        result = backtest_engine.run_backtest(
            strategy,
            data,
            initial_capital=request.initial_capital,
            position_size=request.position_size
        )
        
        return {
            "symbol": request.symbol,
            "strategy": request.strategy,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/backtest/results")
async def get_backtest_results():
    return {
        "results": backtest_engine.results
    }

@app.get("/backtest/compare")
async def compare_strategies():
    if not backtest_engine.results:
        raise HTTPException(status_code=404, detail="no backtest results available")
    
    comparison = backtest_engine.compare_strategies(backtest_engine.results)
    return comparison

# portfolio endpoints
@app.get("/portfolio/summary")
async def get_portfolio_summary():
    try:
        summary = portfolio.get_portfolio_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/portfolio/trade")
async def execute_trade(request: TradeRequest):
    try:
        if request.trade_type == "buy":
            success = portfolio.add_position(
                request.symbol,
                request.quantity,
                request.price
            )
        elif request.trade_type == "sell":
            success = portfolio.remove_position(
                request.symbol,
                request.quantity,
                request.price
            )
        else:
            raise HTTPException(status_code=400, detail="invalid trade type")
        
        if success:
            # save trade to database
            save_trade(
                request.symbol,
                request.trade_type,
                request.quantity,
                request.price,
                request.quantity * request.price,
                strategy="manual"
            )
            
            return {
                "status": "success",
                "message": f"{request.trade_type} order executed"
            }
        else:
            return {
                "status": "failed",
                "message": "trade execution failed"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/positions")
async def get_positions():
    try:
        positions = portfolio.positions
        return {
            "positions": positions,
            "total_positions": len(positions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/portfolio/performance")
async def get_portfolio_performance():
    try:
        metrics = portfolio.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# paper trading endpoints
@app.post("/paper-trading/start")
async def start_paper_trading():
    try:
        if paper_trading_engine.is_running:
            return {"status": "already_running", "message": "paper trading is already running"}
        
        # start paper trading in background
        asyncio.create_task(paper_trading_engine.run_live_trading())
        
        return {
            "status": "started",
            "message": "paper trading started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/paper-trading/stop")
async def stop_paper_trading():
    try:
        paper_trading_engine.stop_trading()
        return {
            "status": "stopped",
            "message": "paper trading stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/paper-trading/status")
async def get_paper_trading_status():
    try:
        return {
            "is_running": paper_trading_engine.is_running,
            "strategies": list(paper_trading_engine.strategies.keys()),
            "data_feeds": list(paper_trading_engine.data_feeds.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/paper-trading/performance")
async def get_paper_trading_performance():
    try:
        report = paper_trading_engine.get_performance_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# indicators endpoints
@app.post("/indicators/calculate")
async def calculate_indicators(request: SymbolRequest):
    try:
        data = data_feed.get_historical_data(
            request.symbol,
            request.period,
            request.interval
        )
        
        if data is None:
            raise HTTPException(status_code=404, detail="no data found for symbol")
        
        indicators = TechnicalIndicators()
        data_with_indicators = indicators.calculate_all_indicators(data)
        
        return {
            "symbol": request.symbol,
            "data_points": len(data_with_indicators),
            "indicators": data_with_indicators.to_dict('records')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# websocket endpoint for live data
@app.websocket("/ws/live-data")
async def websocket_live_data(websocket):
    await websocket.accept()
    
    try:
        while True:
            # send live data for major symbols
            symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
            live_data = {}
            
            for symbol in symbols:
                data = data_feed.get_live_price(symbol)
                if data:
                    live_data[symbol] = data
            
            await websocket.send_json({
                "type": "live_data",
                "data": live_data,
                "timestamp": datetime.now().isoformat()
            })
            
            await asyncio.sleep(5)  # update every 5 seconds
            
    except Exception as e:
        print(f"websocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    print("starting algo trading system...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
