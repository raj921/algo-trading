from peewee import *
from datetime import datetime
import json

# database connection
database = SqliteDatabase('trading_system.db')

class BaseModel(Model):
    class Meta:
        database = database

class Symbol(BaseModel):
    symbol = CharField(unique=True)
    name = CharField()
    exchange = CharField()
    asset_type = CharField()  # stock, crypto, forex
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'symbols'

class Trade(BaseModel):
    symbol = ForeignKeyField(Symbol, backref='trades')
    trade_type = CharField()  # buy, sell
    quantity = FloatField()
    price = FloatField()
    value = FloatField()
    commission = FloatField(default=0.0)
    timestamp = DateTimeField(default=datetime.now)
    strategy = CharField()
    order_id = CharField(null=True)
    
    class Meta:
        table_name = 'trades'

class Position(BaseModel):
    symbol = ForeignKeyField(Symbol, backref='positions')
    shares = FloatField()
    entry_price = FloatField()
    cost_basis = FloatField()
    last_price = FloatField()
    unrealized_pnl = FloatField(default=0.0)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'positions'

class PortfolioSnapshot(BaseModel):
    total_value = FloatField()
    cash = FloatField()
    total_return = FloatField()
    timestamp = DateTimeField(default=datetime.now)
    positions_count = IntegerField(default=0)
    
    class Meta:
        table_name = 'portfolio_snapshots'

class Strategy(BaseModel):
    name = CharField(unique=True)
    description = TextField()
    parameters = TextField()  # json string
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'strategies'

class StrategyPerformance(BaseModel):
    strategy = ForeignKeyField(Strategy, backref='performance')
    symbol = ForeignKeyField(Symbol, backref='strategy_performance')
    total_return = FloatField()
    max_drawdown = FloatField()
    sharpe_ratio = FloatField()
    win_rate = FloatField()
    total_trades = IntegerField()
    start_date = DateTimeField()
    end_date = DateTimeField()
    created_at = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'strategy_performance'

class MarketData(BaseModel):
    symbol = ForeignKeyField(Symbol, backref='market_data')
    timestamp = DateTimeField()
    open_price = FloatField()
    high_price = FloatField()
    low_price = FloatField()
    close_price = FloatField()
    volume = FloatField()
    
    class Meta:
        table_name = 'market_data'
        indexes = (
            (('symbol', 'timestamp'), True),  # unique constraint
        )

class Signal(BaseModel):
    symbol = ForeignKeyField(Symbol, backref='signals')
    strategy = ForeignKeyField(Strategy, backref='signals')
    signal_type = CharField()  # buy, sell, hold
    price = FloatField()
    strength = FloatField()
    reason = TextField()
    timestamp = DateTimeField(default=datetime.now)
    is_executed = BooleanField(default=False)
    
    class Meta:
        table_name = 'signals'

class RiskMetrics(BaseModel):
    portfolio_value = FloatField()
    max_drawdown = FloatField()
    volatility = FloatField()
    var_95 = FloatField()
    sharpe_ratio = FloatField()
    timestamp = DateTimeField(default=datetime.now)
    
    class Meta:
        table_name = 'risk_metrics'

# database utility functions
def create_tables():
    print("creating database tables...")
    database.create_tables([
        Symbol, Trade, Position, PortfolioSnapshot, Strategy, 
        StrategyPerformance, MarketData, Signal, RiskMetrics
    ])
    print("database tables created successfully")

def drop_tables():
    print("dropping database tables...")
    database.drop_tables([
        Symbol, Trade, Position, PortfolioSnapshot, Strategy,
        StrategyPerformance, MarketData, Signal, RiskMetrics
    ])
    print("database tables dropped successfully")

def init_database():
    print("initializing database...")
    create_tables()
    
    # add some default symbols
    default_symbols = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'exchange': 'NASDAQ', 'asset_type': 'stock'},
        {'symbol': 'MSFT', 'name': 'Microsoft Corporation', 'exchange': 'NASDAQ', 'asset_type': 'stock'},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'exchange': 'NASDAQ', 'asset_type': 'stock'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'exchange': 'NASDAQ', 'asset_type': 'stock'},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corporation', 'exchange': 'NASDAQ', 'asset_type': 'stock'},
        {'symbol': 'BTC-USD', 'name': 'Bitcoin', 'exchange': 'CRYPTO', 'asset_type': 'crypto'},
        {'symbol': 'ETH-USD', 'name': 'Ethereum', 'exchange': 'CRYPTO', 'asset_type': 'crypto'}
    ]
    
    for symbol_data in default_symbols:
        symbol, created = Symbol.get_or_create(
            symbol=symbol_data['symbol'],
            defaults=symbol_data
        )
        if created:
            print(f"added symbol: {symbol_data['symbol']}")
    
    # add default strategies
    default_strategies = [
        {
            'name': 'SMA_Crossover',
            'description': 'Simple Moving Average Crossover Strategy',
            'parameters': json.dumps({'fast_period': 20, 'slow_period': 50})
        },
        {
            'name': 'RSI_Momentum',
            'description': 'RSI-based Momentum Strategy',
            'parameters': json.dumps({'rsi_period': 14, 'oversold': 30, 'overbought': 70})
        },
        {
            'name': 'Bollinger_Bands',
            'description': 'Bollinger Bands Mean Reversion Strategy',
            'parameters': json.dumps({'period': 20, 'std_dev': 2})
        }
    ]
    
    for strategy_data in default_strategies:
        strategy, created = Strategy.get_or_create(
            name=strategy_data['name'],
            defaults=strategy_data
        )
        if created:
            print(f"added strategy: {strategy_data['name']}")
    
    print("database initialization completed")

# helper functions for database operations
def save_trade(symbol_str, trade_type, quantity, price, value, commission=0.0, strategy="", order_id=None):
    try:
        symbol = Symbol.get(Symbol.symbol == symbol_str)
        trade = Trade.create(
            symbol=symbol,
            trade_type=trade_type,
            quantity=quantity,
            price=price,
            value=value,
            commission=commission,
            strategy=strategy,
            order_id=order_id
        )
        print(f"saved trade: {trade_type} {quantity} {symbol_str} at ${price}")
        return trade
    except Symbol.DoesNotExist:
        print(f"symbol {symbol_str} not found in database")
        return None

def save_market_data(symbol_str, timestamp, open_price, high_price, low_price, close_price, volume):
    try:
        symbol = Symbol.get(Symbol.symbol == symbol_str)
        market_data, created = MarketData.get_or_create(
            symbol=symbol,
            timestamp=timestamp,
            defaults={
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'volume': volume
            }
        )
        if created:
            print(f"saved market data for {symbol_str} at {timestamp}")
        return market_data
    except Symbol.DoesNotExist:
        print(f"symbol {symbol_str} not found in database")
        return None

def save_signal(symbol_str, strategy_name, signal_type, price, strength, reason):
    try:
        symbol = Symbol.get(Symbol.symbol == symbol_str)
        strategy = Strategy.get(Strategy.name == strategy_name)
        signal = Signal.create(
            symbol=symbol,
            strategy=strategy,
            signal_type=signal_type,
            price=price,
            strength=strength,
            reason=reason
        )
        print(f"saved signal: {signal_type} for {symbol_str} at ${price}")
        return signal
    except (Symbol.DoesNotExist, Strategy.DoesNotExist) as e:
        print(f"error saving signal: {e}")
        return None

def get_latest_positions():
    positions = []
    for position in Position.select():
        symbol_info = position.symbol
        positions.append({
            'symbol': symbol_info.symbol,
            'shares': position.shares,
            'entry_price': position.entry_price,
            'cost_basis': position.cost_basis,
            'last_price': position.last_price,
            'unrealized_pnl': position.unrealized_pnl,
            'created_at': position.created_at,
            'updated_at': position.updated_at
        })
    return positions

def get_trade_history(limit=100):
    trades = []
    for trade in Trade.select().order_by(Trade.timestamp.desc()).limit(limit):
        trades.append({
            'symbol': trade.symbol.symbol,
            'trade_type': trade.trade_type,
            'quantity': trade.quantity,
            'price': trade.price,
            'value': trade.value,
            'commission': trade.commission,
            'timestamp': trade.timestamp,
            'strategy': trade.strategy,
            'order_id': trade.order_id
        })
    return trades

def get_portfolio_history(limit=100):
    snapshots = []
    for snapshot in PortfolioSnapshot.select().order_by(PortfolioSnapshot.timestamp.desc()).limit(limit):
        snapshots.append({
            'total_value': snapshot.total_value,
            'cash': snapshot.cash,
            'total_return': snapshot.total_return,
            'timestamp': snapshot.timestamp,
            'positions_count': snapshot.positions_count
        })
    return snapshots

def get_strategy_performance():
    performances = []
    for perf in StrategyPerformance.select():
        performances.append({
            'strategy': perf.strategy.name,
            'symbol': perf.symbol.symbol,
            'total_return': perf.total_return,
            'max_drawdown': perf.max_drawdown,
            'sharpe_ratio': perf.sharpe_ratio,
            'win_rate': perf.win_rate,
            'total_trades': perf.total_trades,
            'start_date': perf.start_date,
            'end_date': perf.end_date
        })
    return performances

if __name__ == "__main__":
    # test database initialization
    init_database()
    
    # test saving some data
    save_trade('AAPL', 'buy', 10, 150.0, 1500.0, 1.5, 'SMA_Crossover')
    save_market_data('AAPL', datetime.now(), 149.0, 151.0, 148.0, 150.0, 1000000)
    save_signal('AAPL', 'SMA_Crossover', 'buy', 150.0, 75.0, 'fast sma crossed above slow sma')
    
    print("database test completed")
