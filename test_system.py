#!/usr/bin/env python3

import sys
import os
import time
import requests
import json
from datetime import datetime

# add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_api_connection():
    """test if the api is running"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_data_feeds():
    """test data feed functionality"""
    print("\n📊 Testing Data Feeds...")
    
    try:
        # test historical data
        response = requests.post('http://localhost:8000/data/historical', 
                               json={'symbol': 'AAPL', 'period': '30d', 'interval': '1d'})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Historical data fetched: {data['data_points']} data points")
        else:
            print(f"❌ Historical data failed: {response.status_code}")
            return False
        
        # test live data
        response = requests.get('http://localhost:8000/data/live/AAPL')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Live data fetched: ${data['price']:.2f}")
        else:
            print(f"❌ Live data failed: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Data feed test failed: {e}")
        return False

def test_strategies():
    """test strategy endpoints"""
    print("\n🎯 Testing Strategies...")
    
    strategies = [
        {'name': 'sma_crossover', 'endpoint': '/strategies/sma-crossover'},
        {'name': 'rsi_momentum', 'endpoint': '/strategies/rsi-momentum'},
        {'name': 'bollinger_bands', 'endpoint': '/strategies/bollinger-bands'}
    ]
    
    for strategy in strategies:
        try:
            response = requests.post(f'http://localhost:8000{strategy["endpoint"]}',
                                   json={'symbol': 'AAPL', 'strategy_name': strategy['name'], 'parameters': {}})
            if response.status_code == 200:
                print(f"✅ {strategy['name']} strategy created successfully")
            else:
                print(f"❌ {strategy['name']} strategy failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Strategy test failed for {strategy['name']}: {e}")
            return False
    
    return True

def test_backtesting():
    """test backtesting functionality"""
    print("\n📈 Testing Backtesting...")
    
    try:
        response = requests.post('http://localhost:8000/backtest/run',
                               json={
                                   'symbol': 'AAPL',
                                   'strategy': 'sma_crossover',
                                   'period': '90d',
                                   'interval': '1d',
                                   'initial_capital': 10000,
                                   'position_size': 0.1
                               })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backtest completed successfully")
            print(f"   Total Return: {result['result']['total_return']:.2f}%")
            print(f"   Max Drawdown: {result['result']['max_drawdown']:.2f}%")
            print(f"   Total Trades: {result['result']['total_trades']}")
            return True
        else:
            print(f"❌ Backtest failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backtest test failed: {e}")
        return False

def test_portfolio():
    """test portfolio functionality"""
    print("\n💼 Testing Portfolio...")
    
    try:
        # get portfolio summary
        response = requests.get('http://localhost:8000/portfolio/summary')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Portfolio summary retrieved")
            print(f"   Portfolio Value: ${data['portfolio_value']:,.2f}")
            print(f"   Total Return: {data['total_return']:.2f}%")
        else:
            print(f"❌ Portfolio summary failed: {response.status_code}")
            return False
        
        # test trade execution
        response = requests.post('http://localhost:8000/portfolio/trade',
                               json={
                                   'symbol': 'AAPL',
                                   'trade_type': 'buy',
                                   'quantity': 1,
                                   'price': 150.0
                               })
        if response.status_code == 200:
            print("✅ Trade execution test successful")
        else:
            print(f"❌ Trade execution failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Portfolio test failed: {e}")
        return False

def test_paper_trading():
    """test paper trading functionality"""
    print("\n📝 Testing Paper Trading...")
    
    try:
        # check paper trading status
        response = requests.get('http://localhost:8000/paper-trading/status')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Paper trading status retrieved")
            print(f"   Running: {data['is_running']}")
            print(f"   Strategies: {len(data['strategies'])}")
        else:
            print(f"❌ Paper trading status failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Paper trading test failed: {e}")
        return False

def test_indicators():
    """test technical indicators"""
    print("\n📊 Testing Technical Indicators...")
    
    try:
        response = requests.post('http://localhost:8000/indicators/calculate',
                               json={'symbol': 'AAPL', 'period': '30d', 'interval': '1d'})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Indicators calculated successfully")
            print(f"   Data Points: {data['data_points']}")
            if data['indicators']:
                first_point = data['indicators'][0]
                indicators = [key for key in first_point.keys() if key not in ['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
                print(f"   Indicators: {', '.join(indicators[:5])}...")
            return True
        else:
            print(f"❌ Indicators calculation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Indicators test failed: {e}")
        return False

def run_comprehensive_test():
    """run all tests"""
    print("🚀 ALGO TRADING SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("API Connection", test_api_connection),
        ("Data Feeds", test_data_feeds),
        ("Strategies", test_strategies),
        ("Backtesting", test_backtesting),
        ("Portfolio", test_portfolio),
        ("Paper Trading", test_paper_trading),
        ("Technical Indicators", test_indicators)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} test ERROR: {e}")
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    print(f"📈 Success Rate: {(passed / (passed + failed) * 100):.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the system configuration.")
        return False

def main():
    """main function"""
    print("Starting Algo Trading System Test Suite...")
    
    # wait a bit for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(2)
    
    success = run_comprehensive_test()
    
    if success:
        print("\n🚀 System is ready for use!")
        print("🌐 Frontend: http://localhost:3000")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        sys.exit(0)
    else:
        print("\n❌ System tests failed. Please check the logs and configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
