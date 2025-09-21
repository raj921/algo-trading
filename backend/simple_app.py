#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import yfinance as yf
from datetime import datetime

# Create FastAPI app
app = FastAPI(title="Algo Trading System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "data_feed": "connected"
    }

@app.get("/data/live/{symbol}")
async def get_live_price(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        latest = ticker.history(period="1d", interval="1m")
        
        if latest.empty:
            return {"error": "no data available"}
            
        current_price = latest['Close'].iloc[-1]
        volume = latest['Volume'].iloc[-1] if 'Volume' in latest.columns else 0
        
        return {
            'symbol': symbol,
            'price': float(current_price),
            'volume': float(volume),
            'timestamp': datetime.now().isoformat(),
            'high': float(latest['High'].iloc[-1]),
            'low': float(latest['Low'].iloc[-1]),
            'open': float(latest['Open'].iloc[-1])
        }
    except Exception as e:
        return {"error": str(e)}

@app.post("/data/historical")
async def get_historical_data(request: dict):
    try:
        symbol = request.get('symbol', 'AAPL')
        period = request.get('period', '1y')
        interval = request.get('interval', '1d')
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            return {"error": "no data found for symbol"}
        
        data.reset_index(inplace=True)
        if 'Date' in data.columns:
            data.rename(columns={'Date': 'Datetime'}, inplace=True)
        
        return {
            "symbol": symbol,
            "data_points": len(data),
            "data": data.to_dict('records')
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("🚀 Starting Algo Trading System...")
    print("🌐 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "simple_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
