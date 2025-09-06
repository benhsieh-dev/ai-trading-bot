#!/bin/bash

# Install core dependencies first
pip install flask>=2.3.0
pip install gunicorn>=21.0.0
pip install pymongo>=4.0.0
pip install python-dotenv>=1.0.0
pip install requests>=2.31.0
pip install alpaca-trade-api>=3.0.0

# Install lumibot core dependencies
pip install pandas>=2.0.0 numpy>=1.20.0
pip install matplotlib>=3.3.3
pip install yfinance>=0.2.61

# Install lumibot with no-deps to avoid conflicts
pip install --no-deps lumibot>=3.0.0

echo "Dependencies installed successfully"