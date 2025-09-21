#!/usr/bin/env python3

import asyncio
import logging
from app import app
import uvicorn

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    print("=" * 60)
    print("🚀 ALGO TRADING SYSTEM - JARNOX INTERNSHIP")
    print("=" * 60)
    print("📊 Features:")
    print("   • Live data feeds (yfinance)")
    print("   • Multiple trading strategies")
    print("   • Backtesting engine")
    print("   • Paper trading simulation")
    print("   • Real-time dashboard")
    print("   • Risk management")
    print("   • Database logging")
    print("=" * 60)
    print("🌐 Starting server on http://localhost:8000")
    print("📈 Dashboard: http://localhost:3000")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        logger.info("server shutdown requested by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        logger.error(f"server error: {e}")
        raise

if __name__ == "__main__":
    main()
