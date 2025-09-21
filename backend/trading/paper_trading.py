import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional
import json
import asyncio
from ..data.data_feed import DataFeed, MockDataFeed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaperTradingEngine:
    def __init__(self, initial_capital=10000, commission=0.001, slippage=0.0005):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        self.positions = {}  # symbol -> position info
        self.orders = []     # pending orders
        self.trades = []     # executed trades
        self.portfolio_history = []
        
        self.is_running = False
        self.strategies = {}
        self.data_feeds = {}
        
    def add_strategy(self, strategy, symbol, weight=1.0):
        print(f"adding strategy {strategy.__class__.__name__} for {symbol}")
        self.strategies[symbol] = {
            'strategy': strategy,
            'weight': weight,
            'last_signal': None
        }
    
    def add_data_feed(self, symbol, feed_type='yfinance'):
        print(f"adding data feed for {symbol} using {feed_type}")
        
        if feed_type == 'yfinance':
            self.data_feeds[symbol] = DataFeed([symbol])
        elif feed_type == 'mock':
            self.data_feeds[symbol] = MockDataFeed([symbol])
        else:
            raise ValueError(f"unsupported feed type: {feed_type}")
    
    def get_portfolio_value(self, current_prices=None):
        total_value = self.capital
        
        for symbol, position in self.positions.items():
            if current_prices and symbol in current_prices:
                current_price = current_prices[symbol]
            else:
                # use last known price or 0
                current_price = position.get('last_price', 0)
            
            position_value = position['shares'] * current_price
            total_value += position_value
        
        return total_value
    
    def get_portfolio_summary(self, current_prices=None):
        portfolio_value = self.get_portfolio_value(current_prices)
        total_return = (portfolio_value - self.initial_capital) / self.initial_capital * 100
        
        summary = {
            'timestamp': datetime.now(),
            'portfolio_value': portfolio_value,
            'cash': self.capital,
            'total_return': total_return,
            'positions': {},
            'total_trades': len(self.trades)
        }
        
        for symbol, position in self.positions.items():
            if current_prices and symbol in current_prices:
                current_price = current_prices[symbol]
                position_value = position['shares'] * current_price
                position_return = (current_price - position['entry_price']) / position['entry_price'] * 100
                
                summary['positions'][symbol] = {
                    'shares': position['shares'],
                    'entry_price': position['entry_price'],
                    'current_price': current_price,
                    'position_value': position_value,
                    'position_return': position_return,
                    'unrealized_pnl': position_value - position['cost_basis']
                }
        
        return summary
    
    def place_order(self, symbol, order_type, quantity, price=None, order_id=None):
        if not order_id:
            order_id = f"{symbol}_{order_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        order = {
            'order_id': order_id,
            'symbol': symbol,
            'type': order_type,  # 'buy' or 'sell'
            'quantity': quantity,
            'price': price,  # None for market order
            'status': 'pending',
            'timestamp': datetime.now(),
            'filled_quantity': 0,
            'filled_price': None
        }
        
        self.orders.append(order)
        print(f"placed {order_type} order for {quantity} shares of {symbol}")
        return order_id
    
    def execute_order(self, order, current_price):
        symbol = order['symbol']
        order_type = order['type']
        quantity = order['quantity']
        
        # apply slippage
        if order_type == 'buy':
            execution_price = current_price * (1 + self.slippage)
        else:
            execution_price = current_price * (1 - self.slippage)
        
        # calculate commission
        trade_value = quantity * execution_price
        commission_cost = trade_value * self.commission
        
        # check if we have enough capital for buy orders
        if order_type == 'buy':
            total_cost = trade_value + commission_cost
            if total_cost > self.capital:
                print(f"insufficient capital for buy order. need {total_cost}, have {self.capital}")
                order['status'] = 'rejected'
                return False
        
        # check if we have enough shares for sell orders
        if order_type == 'sell':
            if symbol not in self.positions or self.positions[symbol]['shares'] < quantity:
                print(f"insufficient shares for sell order. need {quantity}, have {self.positions.get(symbol, {}).get('shares', 0)}")
                order['status'] = 'rejected'
                return False
        
        # execute the trade
        if order_type == 'buy':
            self.capital -= total_cost
            if symbol in self.positions:
                # average down/up
                old_shares = self.positions[symbol]['shares']
                old_cost_basis = self.positions[symbol]['cost_basis']
                new_cost_basis = old_cost_basis + total_cost
                new_shares = old_shares + quantity
                avg_price = new_cost_basis / new_shares
                
                self.positions[symbol] = {
                    'shares': new_shares,
                    'entry_price': avg_price,
                    'cost_basis': new_cost_basis,
                    'last_price': execution_price
                }
            else:
                self.positions[symbol] = {
                    'shares': quantity,
                    'entry_price': execution_price,
                    'cost_basis': total_cost,
                    'last_price': execution_price
                }
        else:  # sell
            sell_value = trade_value - commission_cost
            self.capital += sell_value
            
            self.positions[symbol]['shares'] -= quantity
            self.positions[symbol]['cost_basis'] -= (quantity * self.positions[symbol]['entry_price'])
            
            if self.positions[symbol]['shares'] <= 0:
                del self.positions[symbol]
        
        # record the trade
        trade = {
            'order_id': order['order_id'],
            'symbol': symbol,
            'type': order_type,
            'quantity': quantity,
            'price': execution_price,
            'value': trade_value,
            'commission': commission_cost,
            'timestamp': datetime.now(),
            'capital_after': self.capital,
            'portfolio_value': self.get_portfolio_value({symbol: execution_price})
        }
        
        self.trades.append(trade)
        
        # update order status
        order['status'] = 'filled'
        order['filled_quantity'] = quantity
        order['filled_price'] = execution_price
        
        print(f"executed {order_type} order: {quantity} shares of {symbol} at ${execution_price:.2f}")
        return True
    
    def process_signals(self, symbol, current_data):
        if symbol not in self.strategies:
            return
        
        strategy_info = self.strategies[symbol]
        strategy = strategy_info['strategy']
        
        # generate signals
        signals = strategy.generate_signals(current_data)
        if not signals:
            return
        
        latest_signal = signals[-1]
        last_signal = strategy_info['last_signal']
        
        # check if we have a new signal
        if last_signal and latest_signal['signal'] == last_signal['signal']:
            return
        
        current_price = latest_signal['price']
        signal_type = latest_signal['signal']
        
        if signal_type == 'buy':
            # calculate position size
            portfolio_value = self.get_portfolio_value({symbol: current_price})
            position_size = portfolio_value * 0.1  # 10% of portfolio
            quantity = int(position_size / current_price)
            
            if quantity > 0:
                order_id = self.place_order(symbol, 'buy', quantity)
                self.execute_order(self.orders[-1], current_price)
        
        elif signal_type == 'sell':
            if symbol in self.positions:
                quantity = self.positions[symbol]['shares']
                if quantity > 0:
                    order_id = self.place_order(symbol, 'sell', quantity)
                    self.execute_order(self.orders[-1], current_price)
        
        # update last signal
        strategy_info['last_signal'] = latest_signal
    
    async def run_live_trading(self, update_interval=30):
        print("starting live paper trading...")
        self.is_running = True
        
        # start data feeds
        for symbol, feed in self.data_feeds.items():
            if hasattr(feed, 'start_live_feed'):
                asyncio.create_task(feed.start_live_feed(update_interval))
            elif hasattr(feed, 'start_mock_feed'):
                asyncio.create_task(feed.start_mock_feed(update_interval))
        
        # subscribe to data updates
        async def data_callback(data):
            symbol = data['symbol']
            current_price = data['price']
            
            # process signals
            current_data = pd.DataFrame([{
                'Datetime': data['timestamp'],
                'Open': data.get('open', current_price),
                'High': data.get('high', current_price),
                'Low': data.get('low', current_price),
                'Close': current_price,
                'Volume': data.get('volume', 1000)
            }])
            
            self.process_signals(symbol, current_data)
            
            # update portfolio history
            portfolio_summary = self.get_portfolio_summary({symbol: current_price})
            self.portfolio_history.append(portfolio_summary)
        
        # subscribe to all data feeds
        for feed in self.data_feeds.values():
            feed.subscribe(data_callback)
        
        # main trading loop
        while self.is_running:
            try:
                await asyncio.sleep(update_interval)
                
                # print portfolio summary
                summary = self.get_portfolio_summary()
                print(f"portfolio value: ${summary['portfolio_value']:.2f} "
                      f"(return: {summary['total_return']:.2f}%) "
                      f"trades: {summary['total_trades']}")
                
            except Exception as e:
                print(f"error in trading loop: {e}")
        
        print("live trading stopped")
    
    def stop_trading(self):
        print("stopping paper trading...")
        self.is_running = False
    
    def get_performance_report(self):
        if not self.portfolio_history:
            return {}
        
        # calculate performance metrics
        initial_value = self.initial_capital
        final_value = self.portfolio_history[-1]['portfolio_value']
        total_return = (final_value - initial_value) / initial_value * 100
        
        # calculate drawdown
        peak_value = initial_value
        max_drawdown = 0
        
        for summary in self.portfolio_history:
            current_value = summary['portfolio_value']
            if current_value > peak_value:
                peak_value = current_value
            
            drawdown = (peak_value - current_value) / peak_value
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # analyze trades
        trade_analysis = self._analyze_trades()
        
        return {
            'initial_capital': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'max_drawdown': max_drawdown * 100,
            'total_trades': len(self.trades),
            'trade_analysis': trade_analysis,
            'portfolio_history': self.portfolio_history
        }
    
    def _analyze_trades(self):
        if not self.trades:
            return {}
        
        buy_trades = [t for t in self.trades if t['type'] == 'buy']
        sell_trades = [t for t in self.trades if t['type'] == 'sell']
        
        total_commission = sum(t['commission'] for t in self.trades)
        
        return {
            'total_trades': len(self.trades),
            'buy_trades': len(buy_trades),
            'sell_trades': len(sell_trades),
            'total_commission': total_commission,
            'avg_trade_size': np.mean([t['value'] for t in self.trades]) if self.trades else 0
        }
    
    def export_results(self, filename=None):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"paper_trading_results_{timestamp}.json"
        
        results = {
            'performance': self.get_performance_report(),
            'trades': self.trades,
            'orders': self.orders,
            'portfolio_history': self.portfolio_history
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"paper trading results exported to {filename}")
        return filename

def test_paper_trading():
    print("testing paper trading engine...")
    
    engine = PaperTradingEngine(initial_capital=10000)
    
    # add mock data feed
    engine.add_data_feed('AAPL', 'mock')
    
    # create a simple strategy
    class SimpleStrategy:
        def generate_signals(self, data):
            return [{
                'signal': 'buy',
                'price': data['Close'].iloc[-1],
                'strength': 50.0,
                'reason': 'test signal'
            }]
    
    strategy = SimpleStrategy()
    engine.add_strategy(strategy, 'AAPL')
    
    # test order placement
    order_id = engine.place_order('AAPL', 'buy', 10, 150.0)
    print(f"placed order: {order_id}")
    
    # test order execution
    order = engine.orders[-1]
    engine.execute_order(order, 150.0)
    
    # check portfolio
    summary = engine.get_portfolio_summary({'AAPL': 155.0})
    print(f"portfolio summary: {summary}")
    
    # test performance report
    report = engine.get_performance_report()
    print(f"performance report: {report}")

if __name__ == "__main__":
    test_paper_trading()
