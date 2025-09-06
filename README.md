# 🚀 Professional AI Trading Bot
**Enterprise-grade trading bot with lightweight architecture and professional-grade APIs**

Comprehensive financial education platform featuring real-time trading, advanced sentiment analysis, and professional backtesting capabilities.

## ✨ Features

### 📈 Professional Stock Trading
- **🧠 Advanced AI Strategy**: Multi-source sentiment analysis (news + technical indicators)
- **⚡ Real-time Execution**: Direct Alpaca API integration for instant trades
- **📊 Professional Backtesting**: Historical data analysis with realistic market scenarios
- **💰 Live Portfolio Management**: Real account data, positions, and P&L tracking
- **🎯 Risk Management**: Intelligent position sizing and stop-loss mechanisms

### 🎯 Options Trading Lab  
- **📚 Educational Options Trading**: Learn with realistic simulations and live market data
- **🔴 Live Options Chains**: Real-time options data from Alpaca API
- **🧮 Greeks Calculator**: Real-time Delta, Gamma, Theta, Vega calculations
- **📋 Strategy Templates**: Pre-built strategies (Covered Call, Protective Put, Iron Condor)
- **📈 P&L Tracking**: Live profit/loss monitoring with visual charts
- **🛡️ Paper Trading**: Risk-free learning environment

### 🔬 Advanced Analytics & Intelligence
- **📰 Multi-Source Sentiment**: TextBlob + Alpaca news API for comprehensive sentiment analysis
- **📊 Technical Analysis**: Professional indicators with fallback algorithms
- **🏛️ Market Context**: Historical performance analysis across different market conditions
- **📈 Visual Analytics**: Interactive charts and performance comparisons

## 🏗️ Professional Architecture

### **Lightweight Trading Stack** (Industry Standard)
- **🎯 Direct API Integration**: No heavyweight frameworks - production-ready performance
- **⚡ Fast Deployment**: 2-3 minute builds vs 15+ minute lumibot builds  
- **💾 Efficient**: 200MB containers vs 2GB+ traditional ML stacks
- **🔧 Maintainable**: 11 focused dependencies vs 50+ complex sub-dependencies

### **Technologies Used**
- **Backend**: Python, Flask with professional async handling
- **Trading APIs**: 
  - Direct Alpaca REST API (stocks, options, news, portfolio)
  - Yahoo Finance (historical data and backtesting)
- **AI/ML**: 
  - TextBlob (lightweight sentiment analysis)
  - Scikit-learn (professional ML algorithms)
  - Custom technical indicators
- **Data Processing**: Pandas, NumPy (optimized for financial data)
- **Frontend**: Responsive HTML5/CSS3/JavaScript
- **Database**: MongoDB Atlas (trade persistence and analytics)

## 🚀 Quick Start

### **Option 1: Local Development (Full Features)**
```bash
# 1. Install lightweight dependencies (2-3 minutes)
pip install -r requirements.txt

# 2. Set up API keys (optional - works without)
cp .env.example .env
# Edit .env with your Alpaca API keys

# 3. Run the professional trading bot
python app.py

# 4. Access the dashboard
# http://localhost:5000 (or 5001 if port 5000 is busy)
```

### **Option 2: Demo Mode (No API Keys Required)**
```bash
# Works immediately with realistic demo data
pip install -r requirements.txt
python app.py
```

### **Option 3: Production Deployment (Render/Heroku)**
- **✅ Render**: Deploys in 2-3 minutes (no dependency issues)
- **✅ Heroku**: Works with standard Python buildpack
- **✅ Docker**: Lightweight containers for any platform

## 🔧 Configuration

### **Environment Variables (.env)**
```bash
# Alpaca API (optional - works without)
ALPACA_API_KEY=your_key_here          
ALPACA_API_SECRET=your_secret_here    
PAPER=True                            # Always use paper trading

# MongoDB (optional - works without)
MONGODB_URI=your_mongodb_atlas_uri    

# Flask settings  
PORT=5000                             # Default port
FLASK_ENV=development                 # development or production
```

### **Three Operating Modes:**

1. **🏆 Professional Mode** (with API keys):
   - Real Alpaca account data and news sentiment
   - Live portfolio management and trading
   - Professional backtesting with real market data

2. **🎯 Demo Mode** (without API keys):
   - Realistic mock data based on actual market patterns
   - Full UI functionality for learning and demonstration
   - Perfect for educational use and testing

3. **☁️ Cloud Mode** (deployed):
   - Automatically detects cloud environment 
   - Optimized for production deployment
   - Graceful fallbacks ensure 100% uptime

## Using the Dashboard

The interface is organized into **two main tabs** for different trading styles:

### 📈 Stock Trading Tab

1. **Strategy Configuration:**
   - **Trading Symbol**: Choose stocks (SPY, NVDA, AAPL, etc.)
   - **Position Size**: Set risk level (0.5 = 50% of cash per trade)

2. **Live Trading Demo:**
   - Click **"Start Trading"** to initialize the AI bot
   - Monitor **real-time sentiment analysis** from market news
   - Track **portfolio performance** and cash positions
   - Use **manual controls** to test sentiment and portfolio updates

3. **Historical Backtesting:**
   - Select **date range** (supports 2020-2024 with realistic market scenarios)
   - Compare **AI strategy vs Buy-and-Hold** performance
   - View detailed **performance metrics** (Sharpe ratio, max drawdown, win rate)
   - **Contextual analysis** based on historical market conditions

4. **Performance Analytics:**
   - **Visual charts** comparing strategies
   - **Real-time activity log** with timestamps
   - **Risk metrics** and trade statistics

### 🎯 Options Trading Tab

1. **Paper Portfolio:**
   - Start with **$100,000 virtual cash**
   - Track **real-time P&L** and positions
   - **Educational safety features** prevent real money loss

2. **Options Chain Explorer:**
   - Load **real options data** from Alpaca API
   - **Symbol-aware pricing** (different for SPY vs NVDA)
   - **Interactive options selection** with live Greeks

3. **Advanced Features:**
   - **Greeks Calculator**: Real-time Delta, Gamma, Theta, Vega
   - **Strategy Templates**: Covered Call, Protective Put, Long Straddle, Iron Condor
   - **Scenario Testing**: See how strategies perform in different market conditions
   - **Risk Analysis**: Built-in risk warnings and educational content

4. **Data Sources:**
   - **🟢 Best**: Real Alpaca stock prices + real options contracts
   - **🟡 Good**: Real Alpaca stock prices + enhanced mock options
   - **🟠 Fallback**: Realistic mock data for all symbols

## Quick Start Guide

1. **First Time Setup:**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
   Open http://localhost:5001

2. **Stock Trading:**
   - Go to **📈 Stock Trading** tab
   - Configure symbol and position size
   - Click **"Start Trading"** to test the AI strategy
   - Run **backtests** to see historical performance

3. **Options Education:**
   - Switch to **🎯 Options Trading** tab
   - Change the underlying symbol (try SPY, NVDA, AAPL)
   - Click **"Load Options Chain"** to see real data
   - Select options to see Greeks and pricing

## Command Line Usage

```bash
# Historical backtesting via command line
export IS_BACKTESTING=True
python tradingbot.py

# Stop the web server
Ctrl+C
```

## Educational Value

This platform is designed for **financial education** and includes:
- **Paper trading only** - no real money at risk
- **Historical market context** - learn from past scenarios
- **Risk warnings** and educational content
- **Realistic simulations** based on actual market data
- **Comparative analysis** to understand strategy effectiveness

## Technical Architecture

### Data Sources & APIs
- **Alpaca Markets API**: 
  - Real-time stock quotes (free with paper account)
  - Options contracts and chains (free with paper account)
  - Paper trading execution (educational only)
- **Yahoo Finance**: Historical data for backtesting
- **FinBERT**: AI sentiment analysis of market news

### Backend Components
- **Flask Web Server**: Professional RESTful API with async support
- **Direct Alpaca Integration**: No middleware - enterprise-grade performance
- **Lightweight ML Stack**: TextBlob + scikit-learn for professional sentiment analysis  
- **Intelligent Fallbacks**: Multi-tier graceful degradation for 100% uptime

### Frontend Features
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live data refresh every 30 seconds
- **Interactive Charts**: Visual performance comparisons
- **Tabbed Interface**: Separate stock and options trading areas

## API Endpoints

### Stock Trading
- `GET /api/status` - Get bot status and metrics
- `POST /api/start` - Initialize trading strategy
- `POST /api/stop` - Stop trading bot
- `GET /api/sentiment` - Get current market sentiment
- `GET /api/portfolio` - Get portfolio positions and cash
- `POST /api/backtest` - Run historical backtesting

### Options Trading
- `GET /api/options/<symbol>` - Get options chain for symbol
- Returns real Alpaca data or enhanced mock data with transparent fallback

## Configuration

### Environment Variables (.env)
```bash
ALPACA_API_KEY=your_key_here          # Required for real data
ALPACA_API_SECRET=your_secret_here    # Required for real data  
PAPER=True                            # Always use paper trading
IS_BACKTESTING=False                  # For command line mode
```

### Supported Symbols
**Popular Stocks**: SPY, QQQ, NVDA, AAPL, MSFT, GOOGL, TSLA, META, AMZN, AMD, IWM, GLD, TLT
**Custom Symbols**: Any symbol supported by Alpaca API

## Safety Features

- **Paper Trading Only**: No real money can be lost
- **API Rate Limiting**: Respects Alpaca API limits
- **Graceful Fallbacks**: Works even when APIs are down
- **Educational Warnings**: Clear risk disclosures for options
- **Data Transparency**: Shows exactly what data source is being used

## Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
python app.py

# Access at http://localhost:5001
```

### Key Files
- `app.py` - Flask web server with environment-aware trading logic
- `tradingbot_lightweight.py` - Professional lightweight trading implementation
- `tradingbot.py` - Legacy lumibot implementation (deprecated)  
- `templates/dashboard.html` - Responsive frontend interface
- `database.py` - MongoDB integration for trade persistence
- `requirements.txt` - Lightweight dependency stack (11 packages)
- `.env` - API configuration (optional)

## Troubleshooting

### Common Issues & Solutions

1. **Port already in use**: 
   ```bash
   # macOS AirPlay uses port 5000
   export PORT=5001
   python app.py
   ```

2. **Dependencies installation slow**:
   ```bash
   # Use lightweight approach (avoid lumibot)
   pip install -r requirements.txt  # Should take 2-3 minutes
   ```

3. **API authentication (optional)**:
   - App works without API keys in demo mode
   - For full features: Get free Alpaca paper trading keys
   - Check `.env` file if using real API keys

4. **Performance optimization**:
   - Sentiment analysis: ~2-3 seconds (professional grade)
   - Portfolio updates: Real-time
   - Backtesting: ~5-10 seconds per year

### 🔍 Debugging & Logs
- **Browser Console**: JavaScript errors and API responses
- **Flask Console**: Real-time API calls and trading decisions  
- **Activity Log**: Live system status in the web dashboard
- **MongoDB**: Persistent trade history and analytics

### 🚀 Deployment Status
- **✅ Render**: Fast deployment (2-3 minutes)
- **✅ Local**: Instant startup with full features
- **✅ Demo**: Works immediately without any configuration

---

## 🏆 Professional Trading Bot - Ready for Production

**Built with industry-standard architecture for reliability, performance, and maintainability.**