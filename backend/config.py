import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # database configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///trading_system.db')
    
    # redis configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # api configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # trading configuration
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 10000))
    COMMISSION_RATE = float(os.getenv('COMMISSION_RATE', 0.001))
    SLIPPAGE = float(os.getenv('SLIPPAGE', 0.0005))
    
    # risk management
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', 0.2))
    MAX_DRAWDOWN_LIMIT = float(os.getenv('MAX_DRAWDOWN_LIMIT', 0.15))
    STOP_LOSS_PCT = float(os.getenv('STOP_LOSS_PCT', 0.05))
    TAKE_PROFIT_PCT = float(os.getenv('TAKE_PROFIT_PCT', 0.15))
    
    # data feed configuration
    DEFAULT_SYMBOLS = [
        'AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 
        'BTC-USD', 'ETH-USD', 'ADA-USD'
    ]
    
    # strategy configuration
    SMA_FAST_PERIOD = int(os.getenv('SMA_FAST_PERIOD', 20))
    SMA_SLOW_PERIOD = int(os.getenv('SMA_SLOW_PERIOD', 50))
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', 30))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', 70))
    BB_PERIOD = int(os.getenv('BB_PERIOD', 20))
    BB_STD_DEV = float(os.getenv('BB_STD_DEV', 2))
    
    # logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/trading_system.log')
    
    # security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    @classmethod
    def validate(cls):
        """validate configuration"""
        required_vars = [
            'DATABASE_URL',
            'REDIS_URL'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"missing required environment variables: {', '.join(missing_vars)}")
        
        return True
