import yfinance as yf
import pandas as pd
import asyncio
import websockets
import json
import time
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataFeed:
    def __init__(self, symbols=None):
        self.symbols = symbols or ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        self.historical_data = {}
        self.live_data = {}
        self.subscribers = []
        
    def get_historical_data(self, symbol, period="1y", interval="1d"):
        print(f"fetching historical data for {symbol}")
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                print(f"no data found for {symbol}")
                return None
                
            data.reset_index(inplace=True)
            if 'Date' in data.columns:
                data.rename(columns={'Date': 'Datetime'}, inplace=True)
            
            self.historical_data[symbol] = data
            print(f"loaded {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            print(f"error fetching data for {symbol}: {e}")
            return None
    
    def get_multiple_symbols(self, symbols=None, period="1y", interval="1d"):
        symbols = symbols or self.symbols
        data_dict = {}
        
        for symbol in symbols:
            data = self.get_historical_data(symbol, period, interval)
            if data is not None:
                data_dict[symbol] = data
                
        return data_dict
    
    def get_live_price(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            latest = ticker.history(period="1d", interval="1m")
            
            if latest.empty:
                return None
                
            current_price = latest['Close'].iloc[-1]
            volume = latest['Volume'].iloc[-1] if 'Volume' in latest.columns else 0
            
            live_data = {
                'symbol': symbol,
                'price': current_price,
                'volume': volume,
                'timestamp': datetime.now(),
                'high': latest['High'].iloc[-1],
                'low': latest['Low'].iloc[-1],
                'open': latest['Open'].iloc[-1]
            }
            
            self.live_data[symbol] = live_data
            return live_data
            
        except Exception as e:
            print(f"error getting live price for {symbol}: {e}")
            return None
    
    def start_live_feed(self, interval=30):
        print(f"starting live data feed with {interval}s interval")
        
        async def live_update():
            while True:
                for symbol in self.symbols:
                    live_data = self.get_live_price(symbol)
                    if live_data:
                        await self._notify_subscribers(live_data)
                await asyncio.sleep(interval)
        
        asyncio.run(live_update())
    
    def subscribe(self, callback):
        self.subscribers.append(callback)
    
    async def _notify_subscribers(self, data):
        for callback in self.subscribers:
            try:
                await callback(data)
            except Exception as e:
                print(f"error in subscriber callback: {e}")

class WebSocketFeed:
    def __init__(self, symbols=None):
        self.symbols = symbols or ["AAPL", "MSFT", "GOOGL"]
        self.connected = False
        self.subscribers = []
    
    async def connect(self):
        try:
            uri = "wss://stream.binance.com:9443/ws/btcusdt@ticker"
            async with websockets.connect(uri) as websocket:
                self.connected = True
                print("connected to binance websocket")
                
                async for message in websocket:
                    data = json.loads(message)
                    await self._process_message(data)
                    
        except Exception as e:
            print(f"websocket connection error: {e}")
            self.connected = False
    
    async def _process_message(self, data):
        if 's' in data and 'c' in data:
            symbol = data['s']
            price = float(data['c'])
            
            live_data = {
                'symbol': symbol,
                'price': price,
                'timestamp': datetime.now(),
                'volume': float(data.get('v', 0)),
                'high': float(data.get('h', 0)),
                'low': float(data.get('l', 0)),
                'open': float(data.get('o', 0))
            }
            
            await self._notify_subscribers(live_data)
    
    def subscribe(self, callback):
        self.subscribers.append(callback)
    
    async def _notify_subscribers(self, data):
        for callback in self.subscribers:
            try:
                await callback(data)
            except Exception as e:
                print(f"error in websocket subscriber: {e}")

class MockDataFeed:
    def __init__(self, symbols=None):
        self.symbols = symbols or ["AAPL", "MSFT", "GOOGL"]
        self.base_prices = {
            "AAPL": 150.0,
            "MSFT": 300.0,
            "GOOGL": 2500.0,
            "TSLA": 200.0,
            "NVDA": 400.0
        }
        self.current_prices = self.base_prices.copy()
        self.subscribers = []
    
    def generate_mock_data(self, symbol):
        import random
        
        if symbol not in self.current_prices:
            self.current_prices[symbol] = 100.0
        
        change_percent = random.uniform(-0.02, 0.02)
        price_change = self.current_prices[symbol] * change_percent
        new_price = self.current_prices[symbol] + price_change
        
        self.current_prices[symbol] = max(new_price, 0.01)
        
        return {
            'symbol': symbol,
            'price': round(self.current_prices[symbol], 2),
            'timestamp': datetime.now(),
            'volume': random.randint(1000, 10000),
            'high': round(self.current_prices[symbol] * 1.01, 2),
            'low': round(self.current_prices[symbol] * 0.99, 2),
            'open': round(self.current_prices[symbol] * random.uniform(0.995, 1.005), 2)
        }
    
    async def start_mock_feed(self, interval=5):
        print(f"starting mock data feed with {interval}s interval")
        
        while True:
            for symbol in self.symbols:
                mock_data = self.generate_mock_data(symbol)
                await self._notify_subscribers(mock_data)
            
            await asyncio.sleep(interval)
    
    def subscribe(self, callback):
        self.subscribers.append(callback)
    
    async def _notify_subscribers(self, data):
        for callback in self.subscribers:
            try:
                await callback(data)
            except Exception as e:
                print(f"error in mock feed subscriber: {e}")

def test_data_feed():
    feed = DataFeed()
    
    print("testing historical data fetch...")
    data = feed.get_historical_data("AAPL", period="30d", interval="1d")
    if data is not None:
        print(f"successfully loaded {len(data)} records")
        print(data[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']].head())
    
    print("\ntesting live price fetch...")
    live_data = feed.get_live_price("AAPL")
    if live_data:
        print(f"live data: {live_data}")

if __name__ == "__main__":
    test_data_feed()