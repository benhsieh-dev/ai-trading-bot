from __future__ import annotations

from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime, timedelta
from alpaca_trade_api import REST
from finbert_utils import estimate_sentiment
import os

# Use environment variables for API keys
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": True
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
        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        cash, last_price, quantity = self.position_sizing()
        if cash > last_price:
            if self.last_trade is None:
                probability, sentiment = self.get_sentiment()
                print(probability, sentiment)
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy"
                )
                self.submit_order(order)

                # Create take profit order
                take_profit_order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    limit_price=last_price * 1.20
                )
                self.submit_order(take_profit_order)

                # Create stop loss order
                stop_loss_order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    stop_price=last_price * 0.95
                )
                self.submit_order(stop_loss_order)

                self.last_trade = "buy"

start_date = datetime(2023, 12, 15)
end_date = datetime(2023, 12, 31)

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='mlstrat', broker=broker, parameters={"symbol": "SPY", "cash_at_risk": 0.5})
strategy.backtest(YahooDataBacktesting, start_date, end_date)