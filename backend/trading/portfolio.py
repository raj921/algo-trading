import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Portfolio:
    def __init__(self, initial_capital=10000, max_positions=10, max_position_size=0.2):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.max_positions = max_positions
        self.max_position_size = max_position_size
        
        self.positions = {}  # symbol -> position info
        self.trades = []
        self.performance_history = []
        
        # risk management
        self.max_drawdown_limit = 0.15  # 15% max drawdown
        self.stop_loss_pct = 0.05       # 5% stop loss
        self.take_profit_pct = 0.15     # 15% take profit
        
    def get_total_value(self, current_prices=None):
        total_value = self.cash
        
        for symbol, position in self.positions.items():
            if current_prices and symbol in current_prices:
                current_price = current_prices[symbol]
            else:
                current_price = position.get('last_price', 0)
            
            position_value = position['shares'] * current_price
            total_value += position_value
        
        return total_value
    
    def get_position_info(self, symbol, current_price=None):
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        current_price = current_price or position.get('last_price', 0)
        
        position_value = position['shares'] * current_price
        unrealized_pnl = position_value - position['cost_basis']
        unrealized_return = unrealized_pnl / position['cost_basis'] * 100
        
        return {
            'symbol': symbol,
            'shares': position['shares'],
            'entry_price': position['entry_price'],
            'current_price': current_price,
            'cost_basis': position['cost_basis'],
            'position_value': position_value,
            'unrealized_pnl': unrealized_pnl,
            'unrealized_return': unrealized_return,
            'weight': position_value / self.get_total_value({symbol: current_price}) * 100
        }
    
    def can_add_position(self, symbol, quantity, price):
        position_value = quantity * price
        current_portfolio_value = self.get_total_value()
        
        # check if we have enough cash
        if position_value > self.cash:
            return False, "insufficient cash"
        
        # check max position size
        if position_value / current_portfolio_value > self.max_position_size:
            return False, f"position size exceeds {self.max_position_size*100}% limit"
        
        # check max positions (if adding new position)
        if symbol not in self.positions and len(self.positions) >= self.max_positions:
            return False, "max positions reached"
        
        return True, "ok"
    
    def add_position(self, symbol, quantity, price, commission=0.001):
        can_add, reason = self.can_add_position(symbol, quantity, price)
        
        if not can_add:
            print(f"cannot add position: {reason}")
            return False
        
        position_value = quantity * price
        commission_cost = position_value * commission
        total_cost = position_value + commission_cost
        
        # check if we have enough cash after commission
        if total_cost > self.cash:
            print(f"insufficient cash after commission. need {total_cost}, have {self.cash}")
            return False
        
        # update cash
        self.cash -= total_cost
        
        # add or update position
        if symbol in self.positions:
            # average down/up
            old_shares = self.positions[symbol]['shares']
            old_cost_basis = self.positions[symbol]['cost_basis']
            
            new_shares = old_shares + quantity
            new_cost_basis = old_cost_basis + total_cost
            avg_price = new_cost_basis / new_shares
            
            self.positions[symbol] = {
                'shares': new_shares,
                'entry_price': avg_price,
                'cost_basis': new_cost_basis,
                'last_price': price,
                'last_update': datetime.now()
            }
        else:
            self.positions[symbol] = {
                'shares': quantity,
                'entry_price': price,
                'cost_basis': total_cost,
                'last_price': price,
                'last_update': datetime.now()
            }
        
        # record trade
        trade = {
            'symbol': symbol,
            'type': 'buy',
            'quantity': quantity,
            'price': price,
            'value': position_value,
            'commission': commission_cost,
            'timestamp': datetime.now()
        }
        self.trades.append(trade)
        
        print(f"added position: {quantity} shares of {symbol} at ${price:.2f}")
        return True
    
    def remove_position(self, symbol, quantity=None, price=None, commission=0.001):
        if symbol not in self.positions:
            print(f"no position found for {symbol}")
            return False
        
        position = self.positions[symbol]
        sell_quantity = quantity or position['shares']
        
        if sell_quantity > position['shares']:
            print(f"cannot sell {sell_quantity} shares, only have {position['shares']}")
            return False
        
        # calculate proceeds
        sell_value = sell_quantity * price
        commission_cost = sell_value * commission
        net_proceeds = sell_value - commission_cost
        
        # update cash
        self.cash += net_proceeds
        
        # update position
        remaining_shares = position['shares'] - sell_quantity
        
        if remaining_shares > 0:
            # partial sell
            cost_per_share = position['cost_basis'] / position['shares']
            remaining_cost_basis = remaining_shares * cost_per_share
            
            self.positions[symbol] = {
                'shares': remaining_shares,
                'entry_price': position['entry_price'],
                'cost_basis': remaining_cost_basis,
                'last_price': price,
                'last_update': datetime.now()
            }
        else:
            # complete sell
            del self.positions[symbol]
        
        # record trade
        trade = {
            'symbol': symbol,
            'type': 'sell',
            'quantity': sell_quantity,
            'price': price,
            'value': sell_value,
            'commission': commission_cost,
            'timestamp': datetime.now()
        }
        self.trades.append(trade)
        
        print(f"removed position: {sell_quantity} shares of {symbol} at ${price:.2f}")
        return True
    
    def rebalance_portfolio(self, target_weights, current_prices):
        print("rebalancing portfolio...")
        
        current_portfolio_value = self.get_total_value(current_prices)
        
        for symbol, target_weight in target_weights.items():
            current_weight = 0
            current_shares = 0
            
            if symbol in self.positions:
                position_info = self.get_position_info(symbol, current_prices[symbol])
                current_weight = position_info['weight']
                current_shares = position_info['shares']
            
            target_value = current_portfolio_value * target_weight
            target_shares = int(target_value / current_prices[symbol])
            
            # calculate difference
            shares_diff = target_shares - current_shares
            
            if shares_diff > 0:
                # need to buy
                self.add_position(symbol, shares_diff, current_prices[symbol])
            elif shares_diff < 0:
                # need to sell
                self.remove_position(symbol, abs(shares_diff), current_prices[symbol])
    
    def check_risk_limits(self, current_prices):
        portfolio_value = self.get_total_value(current_prices)
        total_return = (portfolio_value - self.initial_capital) / self.initial_capital
        
        # check max drawdown
        if len(self.performance_history) > 0:
            peak_value = max([p['portfolio_value'] for p in self.performance_history])
            current_drawdown = (peak_value - portfolio_value) / peak_value
            
            if current_drawdown > self.max_drawdown_limit:
                print(f"max drawdown limit exceeded: {current_drawdown*100:.2f}%")
                return False
        
        # check individual position stop losses
        positions_to_sell = []
        for symbol, position in self.positions.items():
            current_price = current_prices.get(symbol, position.get('last_price', 0))
            entry_price = position['entry_price']
            
            # stop loss check
            price_change = (current_price - entry_price) / entry_price
            if price_change <= -self.stop_loss_pct:
                print(f"stop loss triggered for {symbol}: {price_change*100:.2f}%")
                positions_to_sell.append(symbol)
            
            # take profit check
            elif price_change >= self.take_profit_pct:
                print(f"take profit triggered for {symbol}: {price_change*100:.2f}%")
                positions_to_sell.append(symbol)
        
        # execute stop loss/take profit orders
        for symbol in positions_to_sell:
            self.remove_position(symbol, price=current_prices[symbol])
        
        return True
    
    def update_performance(self, current_prices):
        portfolio_value = self.get_total_value(current_prices)
        total_return = (portfolio_value - self.initial_capital) / self.initial_capital * 100
        
        performance_record = {
            'timestamp': datetime.now(),
            'portfolio_value': portfolio_value,
            'cash': self.cash,
            'total_return': total_return,
            'positions_count': len(self.positions),
            'positions': {}
        }
        
        # add position details
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                position_info = self.get_position_info(symbol, current_prices[symbol])
                performance_record['positions'][symbol] = position_info
        
        self.performance_history.append(performance_record)
        
        return performance_record
    
    def get_performance_metrics(self):
        if not self.performance_history:
            return {}
        
        # calculate basic metrics
        initial_value = self.initial_capital
        final_value = self.performance_history[-1]['portfolio_value']
        total_return = (final_value - initial_value) / initial_value * 100
        
        # calculate returns
        portfolio_values = [p['portfolio_value'] for p in self.performance_history]
        returns = pd.Series(portfolio_values).pct_change().dropna()
        
        # calculate risk metrics
        volatility = returns.std() * np.sqrt(252) * 100 if len(returns) > 1 else 0
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # calculate drawdown
        peak_value = initial_value
        max_drawdown = 0
        
        for value in portfolio_values:
            if value > peak_value:
                peak_value = value
            drawdown = (peak_value - value) / peak_value
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # analyze trades
        trade_analysis = self._analyze_trades()
        
        return {
            'initial_capital': initial_value,
            'final_value': final_value,
            'total_return': total_return,
            'max_drawdown': max_drawdown * 100,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': len(self.trades),
            'trade_analysis': trade_analysis
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
    
    def get_portfolio_summary(self, current_prices=None):
        portfolio_value = self.get_total_value(current_prices)
        total_return = (portfolio_value - self.initial_capital) / self.initial_capital * 100
        
        summary = {
            'timestamp': datetime.now(),
            'portfolio_value': portfolio_value,
            'cash': self.cash,
            'total_return': total_return,
            'positions_count': len(self.positions),
            'positions': {}
        }
        
        for symbol, position in self.positions.items():
            if current_prices and symbol in current_prices:
                position_info = self.get_position_info(symbol, current_prices[symbol])
                summary['positions'][symbol] = position_info
        
        return summary
    
    def export_portfolio(self, filename=None):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolio_{timestamp}.json"
        
        portfolio_data = {
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'positions': self.positions,
            'trades': self.trades,
            'performance_history': self.performance_history,
            'performance_metrics': self.get_performance_metrics()
        }
        
        with open(filename, 'w') as f:
            json.dump(portfolio_data, f, indent=2, default=str)
        
        print(f"portfolio exported to {filename}")
        return filename

def test_portfolio():
    print("testing portfolio management...")
    
    portfolio = Portfolio(initial_capital=10000)
    
    # add some positions
    portfolio.add_position('AAPL', 10, 150.0)
    portfolio.add_position('MSFT', 5, 300.0)
    
    # check portfolio
    current_prices = {'AAPL': 155.0, 'MSFT': 305.0}
    summary = portfolio.get_portfolio_summary(current_prices)
    print(f"portfolio summary: {summary}")
    
    # test risk management
    portfolio.check_risk_limits(current_prices)
    
    # test performance metrics
    portfolio.update_performance(current_prices)
    metrics = portfolio.get_performance_metrics()
    print(f"performance metrics: {metrics}")
    
    # test rebalancing
    target_weights = {'AAPL': 0.6, 'MSFT': 0.4}
    portfolio.rebalance_portfolio(target_weights, current_prices)

if __name__ == "__main__":
    test_portfolio()
