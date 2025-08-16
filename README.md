# Trading Bot
Automate trading using Alpaca API with sentiment analysis

## Technologies Used

- asyncio
- Alpaca API
- FinBERT (sentiment analysis)
- LumiBot
- Python
- Flask (web interface)

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys:**
   - Get your Alpaca API keys from https://alpaca.markets
   - Update `.env` file with your credentials:
   ```
   ALPACA_API_KEY=your_api_key_here
   ALPACA_API_SECRET=your_secret_key_here
   PAPER=True
   IS_BACKTESTING=False
   ```

3. **Start the web server:**
   ```bash
   python app.py
   ```

4. **Open browser to:**
   ```
   http://localhost:5001
   ```

## Using the Web Interface

1. **Configure Bot Settings:**
   - Trading Symbol (default: SPY)
   - Position Size (default: 0.5 = 50% of cash per trade)

2. **Start Trading:**
   - Click "Start Trading" button
   - Bot status will change from "STOPPED" to "RUNNING"

3. **Monitor Performance:**
   - View real-time sentiment analysis
   - Track portfolio cash and positions
   - Monitor trading activity in the log

4. **Manual Controls:**
   - "Update Sentiment" - Get current market sentiment
   - "Refresh Portfolio" - Show current cash and positions
   - "Stop Trading" - Stop the automated bot

5. **Backtesting:**
   - Set start and end years (e.g., 2023 to 2023)
   - Click "Run Backtest" to test strategy on historical data
   - Results will show in terminal and web interface
   - Uses Yahoo Finance data for historical testing

6. **Command Line Backtesting:**
   ```bash
   # Set environment variable
   export IS_BACKTESTING=True
   # Run backtest
   python tradingbot.py
   ```

7. **Stop Trading**
   - Ctrl+C

## Future Considerations