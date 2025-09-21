import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class TechnicalIndicators:
    def __init__(self):
        pass
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        return data.ewm(span=period).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        sma = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        
        return {
            'upper': sma + (std * std_dev),
            'middle': sma,
            'lower': sma - (std * std_dev)
        }
    
    @staticmethod
    def macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, pd.Series]:
        ema_fast = TechnicalIndicators.ema(data, fast_period)
        ema_slow = TechnicalIndicators.ema(data, slow_period)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    @staticmethod
    def stochastic(high: pd.Series, low: pd.Series, close: pd.Series, k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k': k_percent,
            'd': d_percent
        }
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        
        return true_range.rolling(window=period).mean()
    
    @staticmethod
    def williams_r(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        return williams_r
    
    @staticmethod
    def adx(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        atr = TechnicalIndicators.atr(high, low, close, period)
        
        high_diff = high.diff()
        low_diff = low.diff()
        
        plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
        minus_dm = -low_diff.where((low_diff > high_diff) & (low_diff > 0), 0)
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def calculate_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        if 'Close' not in df.columns:
            raise ValueError("dataframe must contain 'Close' column")
        
        close = df['Close']
        
        df['SMA_20'] = TechnicalIndicators.sma(close, 20)
        df['SMA_50'] = TechnicalIndicators.sma(close, 50)
        df['EMA_12'] = TechnicalIndicators.ema(close, 12)
        df['EMA_26'] = TechnicalIndicators.ema(close, 26)
        df['RSI_14'] = TechnicalIndicators.rsi(close, 14)
        
        bb = TechnicalIndicators.bollinger_bands(close, 20, 2)
        df['BB_Upper'] = bb['upper']
        df['BB_Middle'] = bb['middle']
        df['BB_Lower'] = bb['lower']
        df['BB_Width'] = (bb['upper'] - bb['lower']) / bb['middle'] * 100
        
        macd = TechnicalIndicators.macd(close)
        df['MACD'] = macd['macd']
        df['MACD_Signal'] = macd['signal']
        df['MACD_Histogram'] = macd['histogram']
        
        if 'High' in df.columns and 'Low' in df.columns:
            high = df['High']
            low = df['Low']
            
            stoch = TechnicalIndicators.stochastic(high, low, close)
            df['Stoch_K'] = stoch['k']
            df['Stoch_D'] = stoch['d']
            
            df['ATR_14'] = TechnicalIndicators.atr(high, low, close, 14)
            df['Williams_R'] = TechnicalIndicators.williams_r(high, low, close, 14)
            df['ADX_14'] = TechnicalIndicators.adx(high, low, close, 14)
        
        return df

def test_indicators():
    print("testing technical indicators...")
    
    data = pd.DataFrame({
        'Close': [100, 101, 102, 101, 103, 104, 103, 105, 106, 105],
        'High': [101, 102, 103, 102, 104, 105, 104, 106, 107, 106],
        'Low': [99, 100, 101, 100, 102, 103, 102, 104, 105, 104]
    })
    
    indicators = TechnicalIndicators()
    
    sma_5 = indicators.sma(data['Close'], 5)
    print(f"sma(5): {sma_5.tolist()}")
    
    rsi_14 = indicators.rsi(data['Close'], 14)
    print(f"rsi(14): {rsi_14.tolist()}")
    
    bb = indicators.bollinger_bands(data['Close'], 5, 2)
    print(f"bollinger bands upper: {bb['upper'].tolist()}")
    print(f"bollinger bands lower: {bb['lower'].tolist()}")
    
    all_indicators = indicators.calculate_all_indicators(data)
    print(f"\nall indicators calculated. columns: {list(all_indicators.columns)}")

if __name__ == "__main__":
    test_indicators()
