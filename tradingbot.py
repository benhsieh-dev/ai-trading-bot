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
BASE_URL = "https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": os.getenv("PAPER", "True").lower() == "true"  # Convert to boolean
}

class MLTrader(Strategy):
    def initialize(self, symbol: str = "SPY", cash_at_risk: float = 0.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_at_risk = cash_at_risk  # Fixed typo
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def position_sizing(self):
        cash = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(cash * self.cash_at_risk / last_price, 0)
        return cash, last_price, quantity

    def get_dates(self):
        today = self.get_datetime()
        three_days_prior = today - timedelta(days=3)  # Fixed timedelta usage
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')

    def get_sentiment(self):
        today, three_days_prior = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_prior, end=today)
        # news = [ev.__dict__["_raw"]["headline"] for ev in news]
        news = [ev.headline for ev in news]  # Assuming 'headline' is the correct attribute
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()

        if cash > last_price:
            if sentiment == "positive" and probability > .999:
                if self.last_trade == "sell":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price*1.20,
                    stop_loss_price=last_price*.95
                )
                self.submit_order(order)
                self.last_trade = "buy"
            
            elif sentiment == "negative" and probability > .999:
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    type="bracket",
                    take_profit_price=last_price*.8,
                    stop_loss_price=last_price*1.05
                )
                self.submit_order(order)
                self.last_trade = "sell"

# start_date = datetime(2023, 12, 1)
# end_date = datetime(2023, 12, 31)
async def main():
    broker = Alpaca(ALPACA_CREDS)
    strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol": "SPY", "cash_at_risk": 0.5})

    IS_BACKTESTING = os.getenv("IS_BACKTESTING", "False").lower() == "true"

    if IS_BACKTESTING:
        start_date = datetime(2023, 12, 1)
        end_date = datetime(2023, 12, 31)
        strategy.backtest(YahooDataBacktesting, start_date, end_date)
    else:
        trader = Trader()
        trader.add_strategy(strategy)
        trader.run()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as e:
        if str(e).startswith("There is no current event loop in thread"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

    loop.run_until_complete(main())

