import pandas as pd
import numpy as np
from datetime import datetime
import logging
from data.indicators import TechnicalIndicators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RSIMomentumStrategy:
    def __init__(self, rsi_period=14, oversold=30, overbought=70, symbol="AAPL"):
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought
        self.symbol = symbol
        self.position = 0
        self.signals = []
        self.indicators = TechnicalIndicators()
        
    def calculate_indicators(self, data):
        if len(data) < self.rsi_period:
            logger.warning(f"insufficient data for rsi calculation. need {self.rsi_period} periods, got {len(data)}")
            return data
            
        data = data.copy()
        data['rsi'] = self.indicators.rsi(data['Close'], self.rsi_period)
        data['sma_20'] = self.indicators.sma(data['Close'], 20)
        
        return data
    
    def generate_signals(self, data):
        data = self.calculate_indicators(data)
        self.signals = []
        
        if data.empty or 'rsi' not in data.columns:
            logger.error("no rsi data available for signal generation")
            return []
        
        for i, row in data.iterrows():
            signal = {
                'datetime': row['Datetime'] if 'Datetime' in row else i,
                'price': row['Close'],
                'rsi': row.get('rsi', np.nan),
                'sma_20': row.get('sma_20', np.nan),
                'signal': 'hold',
                'strength': 0.0,
                'reason': ''
            }
            
            if pd.isna(signal['rsi']):
                self.signals.append(signal)
                continue
            
            current_price = signal['price']
            current_rsi = signal['rsi']
            current_sma = signal['sma_20']
            
            if pd.isna(current_sma):
                self.signals.append(signal)
                continue
            
            # buy conditions: rsi oversold and price above sma
            if current_rsi < self.oversold and current_price > current_sma:
                signal['signal'] = 'buy'
                signal['strength'] = (self.oversold - current_rsi) / self.oversold * 100
                signal['reason'] = f'rsi oversold ({current_rsi:.1f}) and price above sma'
            
            # sell conditions: rsi overbought and price below sma
            elif current_rsi > self.overbought and current_price < current_sma:
                signal['signal'] = 'sell'
                signal['strength'] = (current_rsi - self.overbought) / (100 - self.overbought) * 100
                signal['reason'] = f'rsi overbought ({current_rsi:.1f}) and price below sma'
            
            # additional momentum signals
            elif current_rsi < 40 and current_price > current_sma * 1.02:
                signal['signal'] = 'buy'
                signal['strength'] = 50.0
                signal['reason'] = 'momentum buy: rsi recovering and price above sma'
                
            elif current_rsi > 60 and current_price < current_sma * 0.98:
                signal['signal'] = 'sell'
                signal['strength'] = 50.0
                signal['reason'] = 'momentum sell: rsi declining and price below sma'
            
            self.signals.append(signal)
        
        logger.info(f"generated {len(self.signals)} rsi momentum signals for {self.symbol}")
        return self.signals
    
    def backtest(self, data, initial_capital=10000, position_size=0.1, stop_loss=0.05, take_profit=0.10):
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
                'rsi': signal.get('rsi', np.nan)
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
        
        return {
            'strategy': 'RSI Momentum',
            'symbol': self.symbol,
            'initial_capital': initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'max_drawdown': max_drawdown * 100,
            'win_rate': win_rate,
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
    
    def get_signal_strength(self, rsi_value):
        if rsi_value < self.oversold:
            return (self.oversold - rsi_value) / self.oversold * 100
        elif rsi_value > self.overbought:
            return (rsi_value - self.overbought) / (100 - self.overbought) * 100
        else:
            return 0

def test_rsi_strategy():
    print("testing rsi momentum strategy...")
    
    # create sample data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    
    data = pd.DataFrame({
        'Datetime': dates,
        'Open': prices,
        'High': prices * 1.01,
        'Low': prices * 0.99,
        'Close': prices,
        'Volume': np.random.randint(1000, 10000, 100)
    })
    
    strategy = RSIMomentumStrategy(symbol="TEST")
    result = strategy.backtest(data, initial_capital=10000)
    
    print(f"backtest results:")
    print(f"total return: {result['total_return']:.2f}%")
    print(f"max drawdown: {result['max_drawdown']:.2f}%")
    print(f"win rate: {result['win_rate']:.2f}%")
    print(f"total trades: {result['total_trades']}")

if __name__ == "__main__":
    test_rsi_strategy()