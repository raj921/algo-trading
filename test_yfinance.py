#!/usr/bin/env python3
"""
Test script to verify yfinance import is working
"""

try:
    import yfinance as yf
    print("✅ SUCCESS: yfinance imported successfully!")
    print(f"Version: {yf.__version__}")

    # Test basic functionality
    ticker = yf.Ticker("AAPL")
    info = ticker.info
    print("✅ SUCCESS: yfinance basic functionality working!")
    print(f"Apple Inc. market cap: ${info.get('marketCap', 'N/A')}")

except ImportError as e:
    print(f"❌ ERROR: Failed to import yfinance: {e}")
except Exception as e:
    print(f"❌ ERROR: yfinance functionality test failed: {e}")