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

## Local Developments

Two-Terminal Setup:

# Terminal 1: Flask Backend
cd /Volumes/Samsung/ai-trading-bot
python app.py
# Runs on http://localhost:5001

# Terminal 2: Angular Frontend
cd /Volumes/Samsung/ai-trading-bot/frontend
ng serve --proxy-config proxy.conf.json
# Runs on http://localhost:4200


