import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SMACrossoverStrategy:
    def __init__(self, fast_period=20, slow_period=50, symbol="AAPL"):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.symbol = symbol
        self.position = 0  # 0: no position, 1: long, -1: short
        self.signals = []

    def calculate_indicators(self, data):
        """calculate sma indicators"""
        if len(data) < self.slow_period:
            logger.warning(f"insufficient data for sma calculation. need {self.slow_period} periods, got {len(data)}")
            return data

        data = data.copy()
        data['sma_fast'] = data['Close'].rolling(window=self.fast_period).mean()
        data['sma_slow'] = data['Close'].rolling(window=self.slow_period).mean()

        return data

    def generate_signals(self, data):
        """generate buy/sell signals based on sma crossover"""
        data = self.calculate_indicators(data)
        self.signals = []

        if data.empty or 'sma_fast' not in data.columns:
            logger.error("no sma data available for signal generation")
            return []

        for i, row in data.iterrows():
            signal = {
                'datetime': row['Datetime'] if 'Datetime' in row else i,
                'price': row['Close'],
                'sma_fast': row.get('sma_fast', np.nan),
                'sma_slow': row.get('sma_slow', np.nan),
                'signal': 'hold',
                'strength': 0.0
            }

            if pd.isna(signal['sma_fast']) or pd.isna(signal['sma_slow']):
                self.signals.append(signal)
                continue

            prev_fast = data['sma_fast'].iloc[i-1] if i > 0 else np.nan
            prev_slow = data['sma_slow'].iloc[i-1] if i > 0 else np.nan

            if pd.isna(prev_fast) or pd.isna(prev_slow):
                self.signals.append(signal)
                continue

            # buy signal: fast sma crosses above slow sma
            if prev_fast <= prev_slow and signal['sma_fast'] > signal['sma_slow']:
                signal['signal'] = 'buy'
                signal['strength'] = (signal['sma_fast'] - signal['sma_slow']) / signal['sma_slow'] * 100

            # sell signal: fast sma crosses below slow sma
            elif prev_fast >= prev_slow and signal['sma_fast'] < signal['sma_slow']:
                signal['signal'] = 'sell'
                signal['strength'] = abs(signal['sma_fast'] - signal['sma_slow']) / signal['sma_slow'] * 100

            self.signals.append(signal)

        logger.info(f"generated {len(self.signals)} signals for {self.symbol}")
        return self.signals

    def backtest(self, data, initial_capital=10000, position_size=0.1):
        """backtest the strategy on historical data"""
        signals = self.generate_signals(data)
        if not signals:
            return {'error': 'no signals generated'}

        capital = initial_capital
        position = 0
        trades = []
        equity_curve = []

        for i, signal in enumerate(signals):
            current_price = signal['price']

            if signal['signal'] == 'buy' and position == 0:
                # buy logic
                buy_amount = capital * position_size
                shares = buy_amount / current_price
                position = shares
                capital -= buy_amount

                trades.append({
                    'datetime': signal['datetime'],
                    'type': 'buy',
                    'price': current_price,
                    'shares': shares,
                    'value': buy_amount,
                    'capital': capital,
                    'total_equity': capital + (position * current_price)
                })

            elif signal['signal'] == 'sell' and position > 0:
                # sell logic
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
                    'total_equity': capital
                })

            # track equity
            current_equity = capital + (position * current_price)
            equity_curve.append({
                'datetime': signal['datetime'],
                'equity': current_equity,
                'capital': capital,
                'position_value': position * current_price
            })

        # final position close
        if position > 0:
            final_price = data['Close'].iloc[-1]
            final_value = position * final_price
            capital += final_value
            position = 0

        # calculate performance metrics
        final_equity = capital
        total_return = (final_equity - initial_capital) / initial_capital * 100
        max_drawdown = self._calculate_drawdown(equity_curve)

        return {
            'strategy': 'SMA Crossover',
            'symbol': self.symbol,
            'initial_capital': initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'total_trades': len(trades),
            'trades': trades,
            'equity_curve': equity_curve
        }

    def _calculate_drawdown(self, equity_curve):
        """calculate maximum drawdown"""
        if not equity_curve:
            return 0

        peak = equity_curve[0]['equity']
        max_dd = 0

        for point in equity_curve:
            if point['equity'] > peak:
                peak = point['equity']
            dd = (peak - point['equity']) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def get_latest_signal(self):
        """get the most recent signal"""
        if not self.signals:
            return None
        return self.signals[-1]