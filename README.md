# AI Trading Bot Dashboard
Comprehensive financial education platform with AI-powered trading strategies and options trading simulation

## Features

### 📈 Stock Trading
- **AI-Driven Strategy**: Uses sentiment analysis to make trading decisions
- **Real-time Market Data**: Live stock quotes via Alpaca API
- **Historical Backtesting**: Compare AI strategy vs buy-and-hold
- **Paper Trading**: Risk-free testing with virtual money
- **Performance Analytics**: Detailed metrics and visualizations

### 🎯 Options Trading Lab  
- **Educational Options Trading**: Learn options with realistic simulations
- **Real Options Data**: Live options chains from Alpaca (with mock fallback)
- **Greeks Calculator**: Delta, Gamma, Theta, Vega calculations
- **Strategy Templates**: Pre-built strategies (Covered Call, Protective Put, etc.)
- **P&L Tracking**: Real-time profit/loss monitoring
- **Risk Management**: Paper trading with educational safety features

### 🔬 Advanced Analytics
- **Market Scenarios**: Historical context for different market conditions
- **Sentiment Analysis**: FinBERT-powered news sentiment scoring
- **Comparative Analysis**: AI strategy vs traditional investing
- **Visual Charts**: Interactive performance and P&L visualizations

## Technologies Used

- **Backend**: Python, Flask, asyncio
- **APIs**: Alpaca Markets (stocks + options), Yahoo Finance (backtesting)
- **AI/ML**: FinBERT sentiment analysis, Black-Scholes options pricing
- **Trading**: LumiBot framework
- **Frontend**: HTML5, CSS3, JavaScript (responsive design)
- **Data**: Real-time market data with intelligent fallbacks

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys:**
   - Get your Alpaca API keys from https://alpaca.markets
   - Copy the example file and add your credentials:
   ```bash
   cp .env.example .env
   ```
   - Edit `.env` file with your actual keys:
   ```bash
   ALPACA_API_KEY=your_actual_api_key_here
   ALPACA_API_SECRET=your_actual_secret_key_here
   PAPER=True
   IS_BACKTESTING=False
   ```
   - **⚠️ IMPORTANT**: Never commit the `.env` file to git

3. **Start the web server:**
   ```bash
   python app.py
   ```

4. **Open browser to:**
   ```
   http://localhost:5001
   ```

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
- **Flask Web Server**: RESTful API endpoints
- **LumiBot Framework**: Trading strategy execution
- **Black-Scholes Model**: Options pricing and Greeks calculation
- **Intelligent Fallbacks**: Graceful degradation when APIs are unavailable

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
- `app.py` - Flask web server and API endpoints
- `tradingbot.py` - AI trading strategy implementation  
- `templates/dashboard.html` - Frontend interface
- `finbert_utils.py` - Sentiment analysis utilities
- `.env` - API configuration (not in repo)

## Troubleshooting

### Common Issues
1. **Port 5001 in use**: macOS AirPlay uses this port, app will show error
2. **API authentication**: Check your Alpaca keys in `.env` file
3. **Options data unavailable**: App gracefully falls back to enhanced mock data
4. **Slow performance**: Sentiment analysis can take time, be patient

### Logs & Debugging
- Check browser console for JavaScript errors
- Monitor Flask output for API errors
- Activity log shows real-time system status