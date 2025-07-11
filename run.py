#!/usr/bin/env python3
"""
Discord Shit Tracker Bot Runner
Production-ready launcher with error handling and monitoring
"""

import asyncio
import sys
import os
import signal
import logging
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'discord',
        'aiohttp'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("📦 Install with: pip install -r requirements.txt")
        sys.exit(1)

def check_environment():
    """Check if required environment variables are set."""
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed, using system environment variables")
    
    required_vars = [
        'DISCORD_BOT_TOKEN',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("📝 Please check your .env file")
        return False
    
    return True

async def run_bot():
    """Run the bot with error handling."""
    try:
        # Import the bot
        from bot import main
        
        print("🚀 Starting Discord Shit Tracker Bot...")
        await main()
        
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        logging.exception("Fatal error occurred")
        return 1
    
    return 0

def main():
    """Main entry point with comprehensive checks."""
    print("🔍 Performing pre-flight checks...")
    
    # Setup signal handlers
    setup_signal_handlers()
    
    # Check Python version
    check_python_version()
    print("✅ Python version compatible")
    
    # Check dependencies
    check_dependencies()
    print("✅ Dependencies installed")
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    print("✅ Environment configured")
    
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot_runner.log'),
            logging.StreamHandler()
        ]
    )
    
    print("🎯 All checks passed, launching bot...")
    
    # Run the bot
    try:
        exit_code = asyncio.run(run_bot())
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 Failed to start bot: {e}")
        logging.exception("Failed to start bot")
        sys.exit(1)

if __name__ == "__main__":
    main()