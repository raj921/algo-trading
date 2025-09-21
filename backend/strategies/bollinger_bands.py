import pandas as pd
import numpy as np
from datetime import datetime
import logging
from data.indicators import TechnicalIndicators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BollingerBandsStrategy:
    def __init__(self, period=20, std_dev=2, symbol="AAPL"):
        self.period = period
        self.std_dev = std_dev
        self.symbol = symbol
        self.position = 0
        self.signals = []
        self.indicators = TechnicalIndicators()
        
    def calculate_indicators(self, data):
        if len(data) < self.period:
            logger.warning(f"insufficient data for bollinger bands. need {self.period} periods, got {len(data)}")
            return data
            
        data = data.copy()
        bb = self.indicators.bollinger_bands(data['Close'], self.period, self.std_dev)
        
        data['bb_upper'] = bb['upper']
        data['bb_middle'] = bb['middle']
        data['bb_lower'] = bb['lower']
        data['bb_width'] = (bb['upper'] - bb['lower']) / bb['middle'] * 100
        
        # calculate bollinger band position
        data['bb_position'] = (data['Close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])
        
        # calculate price momentum
        data['price_change'] = data['Close'].pct_change()
        
        return data
    
    def generate_signals(self, data):
        data = self.calculate_indicators(data)
        self.signals = []
        
        if data.empty or 'bb_upper' not in data.columns:
            logger.error("no bollinger bands data available for signal generation")
            return []
        
        for i, row in data.iterrows():
            signal = {
                'datetime': row['Datetime'] if 'Datetime' in row else i,
                'price': row['Close'],
                'bb_upper': row.get('bb_upper', np.nan),
                'bb_middle': row.get('bb_middle', np.nan),
                'bb_lower': row.get('bb_lower', np.nan),
                'bb_position': row.get('bb_position', np.nan),
                'bb_width': row.get('bb_width', np.nan),
                'signal': 'hold',
                'strength': 0.0,
                'reason': ''
            }
            
            if pd.isna(signal['bb_upper']) or pd.isna(signal['bb_middle']) or pd.isna(signal['bb_lower']):
                self.signals.append(signal)
                continue
            
            current_price = signal['price']
            bb_upper = signal['bb_upper']
            bb_middle = signal['bb_middle']
            bb_lower = signal['bb_lower']
            bb_position = signal['bb_position']
            bb_width = signal['bb_width']
            
            # mean reversion signals
            if current_price <= bb_lower and bb_width > 5:
                # price at or below lower band - potential buy
                signal['signal'] = 'buy'
                signal['strength'] = min(100, (bb_lower - current_price) / bb_lower * 1000)
                signal['reason'] = f'price at lower band ({current_price:.2f} <= {bb_lower:.2f})'
                
            elif current_price >= bb_upper and bb_width > 5:
                # price at or above upper band - potential sell
                signal['signal'] = 'sell'
                signal['strength'] = min(100, (current_price - bb_upper) / bb_upper * 1000)
                signal['reason'] = f'price at upper band ({current_price:.2f} >= {bb_upper:.2f})'
            
            # breakout signals
            elif current_price > bb_upper and bb_position > 1.05:
                # strong breakout above upper band
                signal['signal'] = 'buy'
                signal['strength'] = min(100, (current_price - bb_upper) / bb_upper * 500)
                signal['reason'] = f'bullish breakout above upper band'
                
            elif current_price < bb_lower and bb_position < -0.05:
                # strong breakdown below lower band
                signal['signal'] = 'sell'
                signal['strength'] = min(100, (bb_lower - current_price) / bb_lower * 500)
                signal['reason'] = f'bearish breakdown below lower band'
            
            # squeeze signals (low volatility)
            elif bb_width < 3 and current_price > bb_middle:
                signal['signal'] = 'buy'
                signal['strength'] = 30.0
                signal['reason'] = 'low volatility squeeze, price above middle'
                
            elif bb_width < 3 and current_price < bb_middle:
                signal['signal'] = 'sell'
                signal['strength'] = 30.0
                signal['reason'] = 'low volatility squeeze, price below middle'
            
            # trend following signals
            elif bb_position > 0.8 and current_price > bb_middle:
                signal['signal'] = 'buy'
                signal['strength'] = 40.0
                signal['reason'] = 'trend following: price in upper half of bands'
                
            elif bb_position < 0.2 and current_price < bb_middle:
                signal['signal'] = 'sell'
                signal['strength'] = 40.0
                signal['reason'] = 'trend following: price in lower half of bands'
            
            self.signals.append(signal)
        
        logger.info(f"generated {len(self.signals)} bollinger bands signals for {self.symbol}")
        return self.signals
    
    def backtest(self, data, initial_capital=10000, position_size=0.1, stop_loss=0.08, take_profit=0.15):
        signals = self.generate_signals(data)
        if not signals:
            return {'error': 'no signals generated'}
        
        capital = initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity_curve = []
        max_drawdown = 0
        peak_equity = initial_capital
        
        for i, signal in enumerate(signals):
            current_price = signal['price']
            current_equity = capital + (position * current_price)
            
            # check stop loss and take profit
            if position > 0:
                price_change = (current_price - entry_price) / entry_price
                
                if price_change <= -stop_loss:
                    # stop loss triggered
                    sell_value = position * current_price
                    capital += sell_value
                    position = 0
                    
                    trades.append({
                        'datetime': signal['datetime'],
                        'type': 'sell',
                        'price': current_price,
                        'shares': 0,
                        'value': sell_value,
                        'capital': capital,
                        'total_equity': capital,
                        'reason': 'stop_loss'
                    })
                    
                elif price_change >= take_profit:
                    # take profit triggered
                    sell_value = position * current_price
                    capital += sell_value
                    position = 0
                    
                    trades.append({
                        'datetime': signal['datetime'],
                        'type': 'sell',
                        'price': current_price,
                        'shares': 0,
                        'value': sell_value,
                        'capital': capital,
                        'total_equity': capital,
                        'reason': 'take_profit'
                    })
            
            # execute new signals
            if signal['signal'] == 'buy' and position == 0:
                buy_amount = capital * position_size
                shares = buy_amount / current_price
                position = shares
                entry_price = current_price
                capital -= buy_amount
                
                trades.append({
                    'datetime': signal['datetime'],
                    'type': 'buy',
                    'price': current_price,
                    'shares': shares,
                    'value': buy_amount,
                    'capital': capital,
                    'total_equity': capital + (position * current_price),
                    'reason': signal['reason']
                })
                
            elif signal['signal'] == 'sell' and position > 0:
                sell_value = position * current_price
                capital += sell_value
                position = 0
                
                trades.append({
                    'datetime': signal['datetime'],
                    'type': 'sell',
                    'price': current_price,
                    'shares': 0,
                    'value': sell_value,
                    'capital': capital,
                    'total_equity': capital,
                    'reason': signal['reason']
                })
            
            # update equity curve
            current_equity = capital + (position * current_price)
            equity_curve.append({
                'datetime': signal['datetime'],
                'equity': current_equity,
                'capital': capital,
                'position_value': position * current_price,
                'bb_position': signal.get('bb_position', np.nan),
                'bb_width': signal.get('bb_width', np.nan)
            })
            
            # track drawdown
            if current_equity > peak_equity:
                peak_equity = current_equity
            
            drawdown = (peak_equity - current_equity) / peak_equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # close final position
        if position > 0:
            final_price = data['Close'].iloc[-1]
            final_value = position * final_price
            capital += final_value
            position = 0
        
        # calculate performance metrics
        final_equity = capital
        total_return = (final_equity - initial_capital) / initial_capital * 100
        
        winning_trades = [t for t in trades if t['type'] == 'sell' and t.get('reason') not in ['stop_loss']]
        losing_trades = [t for t in trades if t['type'] == 'sell' and t.get('reason') == 'stop_loss']
        
        win_rate = len(winning_trades) / len([t for t in trades if t['type'] == 'sell']) * 100 if trades else 0
        
        # calculate average trade metrics
        trade_returns = []
        for i in range(1, len(trades), 2):
            if i < len(trades) and trades[i]['type'] == 'sell':
                buy_trade = trades[i-1]
                sell_trade = trades[i]
                trade_return = (sell_trade['price'] - buy_trade['price']) / buy_trade['price']
                trade_returns.append(trade_return)
        
        avg_return = np.mean(trade_returns) * 100 if trade_returns else 0
        
        return {
            'strategy': 'Bollinger Bands Mean Reversion',
            'symbol': self.symbol,
            'initial_capital': initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'max_drawdown': max_drawdown * 100,
            'win_rate': win_rate,
            'avg_trade_return': avg_return,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'trades': trades,
            'equity_curve': equity_curve
        }
    
    def get_latest_signal(self):
        if not self.signals:
            return None
        return self.signals[-1]
    
    def get_volatility_regime(self, bb_width):
        if bb_width > 8:
            return "high_volatility"
        elif bb_width < 3:
            return "low_volatility"
        else:
            return "normal_volatility"

def test_bollinger_strategy():
    print("testing bollinger bands strategy...")
    
    # create sample data with some volatility patterns
    dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
    
    # create price data with different volatility regimes
    prices = [100]
    for i in range(1, 200):
        if i < 50:  # low volatility
            change = np.random.randn() * 0.3
        elif i < 100:  # high volatility
            change = np.random.randn() * 1.5
        else:  # normal volatility
            change = np.random.randn() * 0.8
        
        new_price = prices[-1] * (1 + change/100)
        prices.append(max(new_price, 1))
    
    data = pd.DataFrame({
        'Datetime': dates,
        'Open': prices,
        'High': [p * 1.02 for p in prices],
        'Low': [p * 0.98 for p in prices],
        'Close': prices,
        'Volume': np.random.randint(1000, 10000, 200)
    })
    
    strategy = BollingerBandsStrategy(symbol="TEST")
    result = strategy.backtest(data, initial_capital=10000)
    
    print(f"backtest results:")
    print(f"total return: {result['total_return']:.2f}%")
    print(f"max drawdown: {result['max_drawdown']:.2f}%")
    print(f"win rate: {result['win_rate']:.2f}%")
    print(f"avg trade return: {result['avg_trade_return']:.2f}%")
    print(f"total trades: {result['total_trades']}")

if __name__ == "__main__":
    test_bollinger_strategy()