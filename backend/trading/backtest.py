import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BacktestEngine:
    def __init__(self, initial_capital=10000, commission=0.001, slippage=0.0005):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.results = {}
        
    def run_backtest(self, strategy, data, **kwargs):
        print(f"running backtest for {strategy.__class__.__name__}")
        
        # run strategy backtest
        result = strategy.backtest(data, initial_capital=self.initial_capital, **kwargs)
        
        if 'error' in result:
            print(f"backtest failed: {result['error']}")
            return result
        
        # enhance results with additional metrics
        enhanced_result = self._calculate_performance_metrics(result)
        
        # store results
        strategy_name = strategy.__class__.__name__
        self.results[strategy_name] = enhanced_result
        
        print(f"backtest completed for {strategy_name}")
        print(f"total return: {enhanced_result['total_return']:.2f}%")
        print(f"max drawdown: {enhanced_result['max_drawdown']:.2f}%")
        print(f"sharpe ratio: {enhanced_result['sharpe_ratio']:.2f}")
        
        return enhanced_result
    
    def _calculate_performance_metrics(self, result):
        equity_curve = result.get('equity_curve', [])
        trades = result.get('trades', [])
        
        if not equity_curve:
            return result
        
        # convert equity curve to dataframe for easier calculations
        equity_df = pd.DataFrame(equity_curve)
        equity_df['datetime'] = pd.to_datetime(equity_df['datetime'])
        equity_df.set_index('datetime', inplace=True)
        
        # calculate returns
        equity_df['returns'] = equity_df['equity'].pct_change()
        equity_df['cumulative_returns'] = (1 + equity_df['returns']).cumprod() - 1
        
        # sharpe ratio
        risk_free_rate = 0.02 / 252  # 2% annual risk-free rate
        excess_returns = equity_df['returns'] - risk_free_rate
        sharpe_ratio = excess_returns.mean() / excess_returns.std() * np.sqrt(252) if excess_returns.std() > 0 else 0
        
        # sortino ratio
        downside_returns = equity_df['returns'][equity_df['returns'] < 0]
        sortino_ratio = excess_returns.mean() / downside_returns.std() * np.sqrt(252) if downside_returns.std() > 0 else 0
        
        # calmar ratio
        annual_return = equity_df['returns'].mean() * 252
        calmar_ratio = annual_return / (result.get('max_drawdown', 0) / 100) if result.get('max_drawdown', 0) > 0 else 0
        
        # volatility
        volatility = equity_df['returns'].std() * np.sqrt(252) * 100
        
        # value at risk (var)
        var_95 = np.percentile(equity_df['returns'], 5) * 100
        
        # maximum consecutive losses
        consecutive_losses = self._calculate_consecutive_losses(equity_df['returns'])
        
        # trade analysis
        trade_analysis = self._analyze_trades(trades)
        
        # add enhanced metrics
        result.update({
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'volatility': volatility,
            'var_95': var_95,
            'max_consecutive_losses': consecutive_losses,
            'trade_analysis': trade_analysis,
            'equity_dataframe': equity_df,
            'annual_return': annual_return * 100
        })
        
        return result
    
    def _calculate_consecutive_losses(self, returns):
        consecutive_losses = 0
        max_consecutive = 0
        current_streak = 0
        
        for ret in returns:
            if ret < 0:
                current_streak += 1
                consecutive_losses += 1
            else:
                if current_streak > max_consecutive:
                    max_consecutive = current_streak
                current_streak = 0
        
        return max_consecutive
    
    def _analyze_trades(self, trades):
        if not trades:
            return {}
        
        # separate buy and sell trades
        buy_trades = [t for t in trades if t['type'] == 'buy']
        sell_trades = [t for t in trades if t['type'] == 'sell']
        
        # calculate trade returns
        trade_returns = []
        trade_durations = []
        
        for i in range(min(len(buy_trades), len(sell_trades))):
            buy_trade = buy_trades[i]
            sell_trade = sell_trades[i]
            
            if sell_trade['datetime'] > buy_trade['datetime']:
                trade_return = (sell_trade['price'] - buy_trade['price']) / buy_trade['price']
                trade_returns.append(trade_return)
                
                # calculate duration
                buy_time = pd.to_datetime(buy_trade['datetime'])
                sell_time = pd.to_datetime(sell_trade['datetime'])
                duration = (sell_time - buy_time).days
                trade_durations.append(duration)
        
        if not trade_returns:
            return {}
        
        # analyze returns
        winning_trades = [r for r in trade_returns if r > 0]
        losing_trades = [r for r in trade_returns if r < 0]
        
        analysis = {
            'total_trades': len(trade_returns),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(winning_trades) / len(trade_returns) * 100,
            'avg_return': np.mean(trade_returns) * 100,
            'avg_winning_return': np.mean(winning_trades) * 100 if winning_trades else 0,
            'avg_losing_return': np.mean(losing_trades) * 100 if losing_trades else 0,
            'max_win': np.max(trade_returns) * 100 if trade_returns else 0,
            'max_loss': np.min(trade_returns) * 100 if trade_returns else 0,
            'profit_factor': abs(np.sum(winning_trades) / np.sum(losing_trades)) if losing_trades and np.sum(losing_trades) != 0 else float('inf'),
            'avg_trade_duration': np.mean(trade_durations) if trade_durations else 0
        }
        
        return analysis
    
    def compare_strategies(self, strategies_data):
        print("comparing strategies...")
        
        comparison = {
            'strategies': [],
            'metrics': {
                'total_return': [],
                'max_drawdown': [],
                'sharpe_ratio': [],
                'win_rate': [],
                'volatility': []
            }
        }
        
        for strategy_name, result in strategies_data.items():
            comparison['strategies'].append(strategy_name)
            comparison['metrics']['total_return'].append(result.get('total_return', 0))
            comparison['metrics']['max_drawdown'].append(result.get('max_drawdown', 0))
            comparison['metrics']['sharpe_ratio'].append(result.get('sharpe_ratio', 0))
            comparison['metrics']['win_rate'].append(result.get('trade_analysis', {}).get('win_rate', 0))
            comparison['metrics']['volatility'].append(result.get('volatility', 0))
        
        # find best performing strategy for each metric
        best_strategies = {}
        for metric, values in comparison['metrics'].items():
            if metric == 'max_drawdown':  # lower is better
                best_idx = np.argmin(values)
            else:  # higher is better
                best_idx = np.argmax(values)
            
            best_strategies[metric] = {
                'strategy': comparison['strategies'][best_idx],
                'value': values[best_idx]
            }
        
        comparison['best_strategies'] = best_strategies
        
        print("strategy comparison completed")
        return comparison
    
    def export_results(self, filename=None):
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backtest_results_{timestamp}.json"
        
        # prepare results for json export
        export_data = {}
        for strategy_name, result in self.results.items():
            export_data[strategy_name] = {
                'total_return': result.get('total_return', 0),
                'max_drawdown': result.get('max_drawdown', 0),
                'sharpe_ratio': result.get('sharpe_ratio', 0),
                'volatility': result.get('volatility', 0),
                'total_trades': result.get('total_trades', 0),
                'trade_analysis': result.get('trade_analysis', {}),
                'annual_return': result.get('annual_return', 0)
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"results exported to {filename}")
        return filename
    
    def generate_report(self):
        print("\n" + "="*60)
        print("BACKTEST PERFORMANCE REPORT")
        print("="*60)
        
        for strategy_name, result in self.results.items():
            print(f"\n{strategy_name.upper()}")
            print("-" * 40)
            
            # basic metrics
            print(f"total return: {result.get('total_return', 0):.2f}%")
            print(f"annual return: {result.get('annual_return', 0):.2f}%")
            print(f"max drawdown: {result.get('max_drawdown', 0):.2f}%")
            print(f"volatility: {result.get('volatility', 0):.2f}%")
            
            # risk metrics
            print(f"sharpe ratio: {result.get('sharpe_ratio', 0):.2f}")
            print(f"sortino ratio: {result.get('sortino_ratio', 0):.2f}")
            print(f"calmar ratio: {result.get('calmar_ratio', 0):.2f}")
            print(f"var 95%: {result.get('var_95', 0):.2f}%")
            
            # trade metrics
            trade_analysis = result.get('trade_analysis', {})
            print(f"total trades: {trade_analysis.get('total_trades', 0)}")
            print(f"win rate: {trade_analysis.get('win_rate', 0):.2f}%")
            print(f"profit factor: {trade_analysis.get('profit_factor', 0):.2f}")
            print(f"avg trade return: {trade_analysis.get('avg_return', 0):.2f}%")
            print(f"avg trade duration: {trade_analysis.get('avg_trade_duration', 0):.1f} days")
        
        print("\n" + "="*60)

def test_backtest_engine():
    print("testing backtest engine...")
    
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
    
    # test with dummy strategy
    class DummyStrategy:
        def backtest(self, data, **kwargs):
            return {
                'strategy': 'Dummy',
                'symbol': 'TEST',
                'initial_capital': 10000,
                'final_equity': 10500,
                'total_return': 5.0,
                'max_drawdown': 2.0,
                'total_trades': 10,
                'trades': [],
                'equity_curve': [
                    {'datetime': dates[i], 'equity': 10000 + i*5, 'capital': 10000, 'position_value': i*5}
                    for i in range(len(dates))
                ]
            }
    
    engine = BacktestEngine()
    strategy = DummyStrategy()
    result = engine.run_backtest(strategy, data)
    
    print(f"backtest result keys: {list(result.keys())}")
    engine.generate_report()

if __name__ == "__main__":
    test_backtest_engine()
