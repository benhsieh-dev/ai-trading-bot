# Trading Bot
**Trading bot with lightweight architecture and professional-grade APIs**
- featuring real-time trading, sentiment analysis, and backtesting capabilities.

## Features

### Stock Trading
- **AI Strategy**: Multi-source sentiment analysis (news + technical indicators)
- **Real-time Execution**: Direct Alpaca API integration for instant trades
- **Backtesting**: Historical data analysis with realistic market scenarios
- **Live Portfolio Management**: Real account data, positions, and P&L tracking
- **Risk Management**: Pposition sizing and stop-loss mechanisms

### Options Trading Lab  
- **Options Trading**: Learn with realistic simulations and live market data
- **Live Options Chains**: Real-time options data from Alpaca API
- **Greeks Calculator**: Real-time Delta, Gamma, Theta, Vega calculations
- **Strategy Templates**: Pre-built strategies (Covered Call, Protective Put, Iron Condor)
- **P&L Tracking**: Live profit/loss monitoring with visual charts
- **Paper Trading**: Risk-free learning environment

### Analytics 
- **Multi-Source Sentiment**: TextBlob + Alpaca news API for comprehensive sentiment analysis
- **Technical Analysis**: Indicators with fallback algorithms
- **Market Context**: Historical performance analysis across different market conditions
- **Visual Analytics**: Interactive charts and performance comparisons


### **Technologies Used**
- **Backend**: Python, Flask with async handling
- **Trading APIs**: 
  - Direct Alpaca REST API (stocks, options, news, portfolio)
  - Yahoo Finance (historical data and backtesting)
- **AI/ML**: 
  - TextBlob (lightweight sentiment analysis)
  - Scikit-learn (professional ML algorithms)
  - Custom technical indicators
- **Data Processing**: Pandas, NumPy (optimized for financial data)
- **Frontend**: Responsive HTML5/CSS3/JavaScript, Angular (transition in progress)
- **Database**: MongoDB Atlas (trade persistence and analytics)


# Flask settings  
PORT=5000                             # Default port
FLASK_ENV=development                 # development or production
```

### **Three Operating Modes:**

1. **Professional Mode** (with API keys):
   - Real Alpaca account data and news sentiment
   - Live portfolio management and trading
   - Professional backtesting with real market data

2. **Demo Mode** (without API keys):
   - Realistic mock data based on actual market patterns
   - Full UI functionality for learning and demonstration
   - Perfect for educational use and testing

3. **Cloud Mode** (deployed):
   - Automatically detects cloud environment 
   - Optimized for production deployment
   - Graceful fallbacks ensure 100% uptime

## Using the Dashboard

The interface is organized into **two main tabs** for different trading styles:

### Stock Trading Tab

1. **Live Trading Demo:**
   - Click **"Start Trading"** to initialize the AI bot
   - Monitor **real-time sentiment analysis** from market news
   - Track **portfolio performance** and cash positions
   - Use **manual controls** to test sentiment and portfolio updates

### Options Trading Tab

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
   - Real Alpaca stock prices + real options contracts
   - Real Alpaca stock prices + enhanced mock options
   - Realistic mock data for all symbols
  
### Sentiment & Backtesting tab
1. **Historical Backtesting:**
   - Select **date range** (supports 2020-2024 with realistic market scenarios)
   - Compare **AI strategy vs Buy-and-Hold** performance
   - View detailed **performance metrics** (Sharpe ratio, max drawdown, win rate)
   - **Contextual analysis** based on historical market conditions

2. **Performance Analytics:**
   - **Visual charts** comparing strategies
   - **Real-time activity log** with timestamps
   - **Risk metrics** and trade statistics

## Quick Start Guide

1. **First Time Setup:**
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
   Open http://localhost:5001

python app.py
ng serve --proxy-config proxy.config.json

http://localhost:5001 # Flask
http://localhost:4200 # Angular (in progress)

2. **Stock Trading:**
   - Go to **📈 Stock Trading** tab
   - Look up stock symbol and place trade
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


### Stock Trading
- `GET /api/status` - Get bot status and metrics
- `POST /api/start` - Initialize trading strategy
- `POST /api/stop` - Stop trading bot
- `GET /api/sentiment` - Get current market sentiment
- `GET /api/sentiment/<symbol>` - Get sentiment analysis for specific symbol
- `GET /api/news/<symbol>` - Get news headlines with sentiment analysis
- `GET /api/portfolio` - Get portfolio positions and cash
- `POST /api/backtest` - Run historical backtesting

### Manual Trading
- `GET /api/price/<symbol>` - Get real-time stock price with cross-validation
- `POST /api/trade` - Place manual buy/sell orders (paper trading)
- `GET /api/orders` - Get all orders (pending and filled)
- `DELETE /api/orders/<order_id>` - Cancel specific order
- `POST /api/orders/cancel-all` - Cancel all pending orders

### Options Trading
- `GET /api/options/<symbol>` - Get options chain for symbol
- Returns real Alpaca data or enhanced mock data with transparent fallback

### Pages
- `GET /` - Main dashboard with trading controls and analytics
- `GET /portfolio` - Comprehensive portfolio management page with detailed positions



## Safety Features

- **Paper Trading Only**: No real money can be lost
- **API Rate Limiting**: Respects Alpaca API limits
- **Graceful Fallbacks**: Works even when APIs are down
- **Educational Warnings**: Clear risk disclosures for options
- **Data Transparency**: Shows exactly what data source is being used




