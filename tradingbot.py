from __future__ import annotations 

import asyncio


from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime, timedelta
from alpaca_trade_api import REST
from finbert_utils import estimate_sentiment

from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env")  # Explicitly specify the path

# Use environment variables for API keys
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets/v2"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": os.getenv("PAPER", "True").lower() == "true"  # Convert to boolean
}

class MLTrader(Strategy):
    def initialize(self, symbol: str = "QQQ", position_size: float = 0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.position_size = position_size  
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.position_size / last_price, 0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - timedelta(days=3)  
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        news = [ev.headline for ev in news]  
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        if cash > last_price:
            if sentiment == "positive" and probability > .700:
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price*2.00,
                    stop_loss_price=last_price*.50
                )
                self.submit_order(order)
                self.last_trade = "buy"
                
            elif sentiment == "negative" and probability > .999:    
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price*2,
                    stop_loss_price=last_price*.50
                )
                self.submit_order(order)
                self.last_trade = "buy"

async def main():
    broker = Alpaca(ALPACA_CREDS)
    strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol": "SPY", "position_size": 0.5})

    IS_BACKTESTING = os.getenv("IS_BACKTESTING", "False").lower() == "true"

    if IS_BACKTESTING:
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 31)
        strategy.backtest(YahooDataBacktesting, start_date, end_date)
    else:
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if str(e).startswith("There is no current event loop in thread"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

    loop.run_until_complete(main())

