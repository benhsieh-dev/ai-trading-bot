"""
Professional Lightweight Trading Bot
Uses direct APIs instead of heavy frameworks like lumibot
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from alpaca_trade_api import REST
from textblob import TextBlob
import requests
from typing import Tuple, Optional, List, Dict
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import database manager for trade persistence
try:
    from database import db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("Database module not available - trades will not be persisted")

# Alpaca credentials
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets" if os.getenv("PAPER", "True").lower() == "true" else "https://api.alpaca.markets"

class LightweightMLTrader:
    """Professional trading bot using lightweight libraries"""
    
    def __init__(self, symbol: str = "SPY", position_size: float = 0.5):
        self.symbol = symbol.upper()
        self.position_size = position_size
        self.last_trade = None
        
        # Initialize Alpaca API client
        self.api = REST(
            key_id=API_KEY,
            secret_key=API_SECRET,
            base_url=BASE_URL,
            api_version='v2'
        )
        
        # Verify connection
        try:
            account = self.api.get_account()
            print(f"✅ Connected to Alpaca - Account: ${float(account.cash):.2f} cash")
        except Exception as e:
            print(f"❌ Alpaca connection failed: {e}")
            
    def get_account_info(self) -> Dict:
        """Get current account information"""
        try:
            account = self.api.get_account()
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'day_trade_count': getattr(account, 'day_trade_count', 0)  # Safe access with default
            }
        except Exception as e:
            print(f"Error getting account info: {e}")
            return {'cash': 0, 'portfolio_value': 0, 'buying_power': 0, 'day_trade_count': 0}
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            positions = self.api.list_positions()
            print(f"Raw positions from Alpaca: {len(positions)} positions found")
            
            formatted_positions = []
            for pos in positions:
                print(f"Position: {pos.symbol} - {pos.qty} shares @ ${pos.avg_entry_price}")
                formatted_positions.append({
                    'symbol': pos.symbol,
                    'quantity': int(pos.qty),
                    'side': 'long' if int(pos.qty) > 0 else 'short',
                    'market_value': float(pos.market_value),
                    'unrealized_pl': float(pos.unrealized_pl),
                    'unrealized_plpc': float(pos.unrealized_plpc) * 100,
                    'avg_entry_price': float(pos.avg_entry_price)
                })
            
            return formatted_positions
        except Exception as e:
            print(f"Error getting positions: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_current_price(self, symbol: str = None) -> float:
        """Get current market price for symbol with cross-validation"""
        symbol = symbol or self.symbol
        
        alpaca_price = None
        yahoo_price = None
        
        # Try to get price from both sources
        try:
            quote = self.api.get_latest_quote(symbol)
            alpaca_price = float(quote.ask_price) if quote.ask_price > 0 else float(quote.bid_price)
            if alpaca_price > 0:
                print(f"Alpaca price for {symbol}: ${alpaca_price:.2f}")
        except Exception as e:
            print(f"Alpaca API failed for {symbol}: {e}")
        
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")['Close'].iloc[-1]
            yahoo_price = float(price)
            print(f"Yahoo Finance price for {symbol}: ${yahoo_price:.2f}")
        except Exception as e:
            print(f"Yahoo Finance failed for {symbol}: {e}")
        
        # Cross-validation logic
        if alpaca_price and yahoo_price:
            # Calculate percentage difference
            price_diff = abs(alpaca_price - yahoo_price) / yahoo_price * 100
            
            if price_diff < 5:  # If prices are within 5%, use Alpaca (more real-time)
                print(f"Prices match (diff: {price_diff:.1f}%), using Alpaca: ${alpaca_price:.2f}")
                return alpaca_price
            else:
                print(f"Price discrepancy (diff: {price_diff:.1f}%), using Yahoo Finance: ${yahoo_price:.2f}")
                return yahoo_price
        
        # Fallback to whichever source worked
        if alpaca_price:
            print(f"Only Alpaca available: ${alpaca_price:.2f}")
            return alpaca_price
        elif yahoo_price:
            print(f"Only Yahoo Finance available: ${yahoo_price:.2f}")
            return yahoo_price
        
        return 0.0
    
    def get_market_data(self, symbol: str = None, period: str = "5d") -> pd.DataFrame:
        """Get historical market data for analysis"""
        symbol = symbol or self.symbol
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data
        except Exception as e:
            print(f"Error getting market data: {e}")
            return pd.DataFrame()
    
    def get_news_sentiment(self, days_back: int = 3) -> Tuple[float, str]:
        """Get sentiment analysis from recent news"""
        try:
            # Get news from Alpaca
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            news = self.api.get_news(
                symbols=self.symbol,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                limit=50
            )
            
            if not news:
                return 0.5, "neutral"
            
            # Analyze sentiment using TextBlob
            sentiments = []
            for article in news:
                headline_sentiment = TextBlob(article.headline).sentiment.polarity
                
                # Weight recent news more heavily
                age_hours = (datetime.now() - article.created_at.replace(tzinfo=None)).total_seconds() / 3600
                weight = max(0.1, 1 - (age_hours / 72))  # Decay over 3 days
                
                sentiments.append(headline_sentiment * weight)
            
            if sentiments:
                avg_sentiment = np.mean(sentiments)
                confidence = min(0.95, abs(avg_sentiment) + 0.5)  # Convert to confidence score
                
                if avg_sentiment > 0.1:
                    return confidence, "bullish"
                elif avg_sentiment < -0.1:
                    return confidence, "bearish"
                else:
                    return confidence, "neutral"
            
            return 0.5, "neutral"
            
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            # Fallback to technical analysis sentiment
            return self.get_technical_sentiment()
    
    def get_technical_sentiment(self) -> Tuple[float, str]:
        """Fallback sentiment based on technical indicators"""
        try:
            data = self.get_market_data(period="30d")
            if data.empty:
                return 0.5, "neutral"
            
            # Simple technical indicators
            current_price = data['Close'].iloc[-1]
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_5 = data['Close'].rolling(5).mean().iloc[-1]
            
            # RSI-like momentum
            price_changes = data['Close'].pct_change().dropna()
            recent_momentum = price_changes.tail(5).mean()
            
            # Combine signals
            trend_signal = 1 if current_price > sma_20 else -1
            short_term_signal = 1 if sma_5 > sma_20 else -1
            momentum_signal = 1 if recent_momentum > 0.01 else (-1 if recent_momentum < -0.01 else 0)
            
            combined_signal = (trend_signal + short_term_signal + momentum_signal) / 3
            confidence = min(0.85, abs(combined_signal) + 0.4)
            
            if combined_signal > 0.3:
                return confidence, "bullish"
            elif combined_signal < -0.3:
                return confidence, "bearish"
            else:
                return confidence, "neutral"
                
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return 0.5, "neutral"
    
    def calculate_position_size(self) -> Tuple[float, int]:
        """Calculate optimal position size based on available cash"""
        try:
            account = self.get_account_info()
            current_price = self.get_current_price()
            
            if current_price <= 0:
                return 0, 0
            
            # Use buying power but cap at cash for safety
            available_cash = min(account['cash'], account['buying_power']) * 0.95  # 5% buffer
            max_position_value = available_cash * self.position_size
            
            quantity = int(max_position_value / current_price)
            actual_cost = quantity * current_price
            
            return actual_cost, quantity
            
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return 0, 0
    
    def place_order(self, side: str, quantity: int, order_type: str = "market") -> Optional[Dict]:
        """Place a trading order"""
        if quantity <= 0:
            print("Invalid quantity for order")
            return None
            
        try:
            order = self.api.submit_order(
                symbol=self.symbol,
                qty=quantity,
                side=side,
                type=order_type,
                time_in_force='day'
            )
            
            order_data = {
                'id': order.id,
                'symbol': order.symbol,
                'side': order.side,
                'quantity': int(order.qty),
                'type': order.type,
                'status': order.status
            }
            
            print(f"✅ Order placed: {side.upper()} {quantity} {self.symbol}")
            
            # Save to database
            if DB_AVAILABLE and db_manager.is_connected():
                trade_data = {
                    "symbol": self.symbol,
                    "side": side,
                    "quantity": quantity,
                    "price": self.get_current_price(),
                    "timestamp": datetime.now(),
                    "order_id": order.id
                }
                db_manager.save_trade(trade_data)
            
            return order_data
            
        except Exception as e:
            print(f"❌ Order failed: {e}")
            return None
    
    def run_trading_logic(self) -> Dict:
        """Main trading logic - returns decision information"""
        try:
            # Get current market state
            probability, sentiment = self.get_news_sentiment()
            current_price = self.get_current_price()
            cost, quantity = self.calculate_position_size()
            
            decision = {
                'timestamp': datetime.now(),
                'symbol': self.symbol,
                'current_price': current_price,
                'sentiment': sentiment,
                'probability': probability,
                'position_cost': cost,
                'quantity': quantity,
                'action': 'hold',
                'reason': 'No clear signal'
            }
            
            # Trading logic
            if quantity > 0 and cost > 0:
                # Bullish signal - buy
                if sentiment == "bullish" and probability > 0.70:
                    order = self.place_order("buy", quantity)
                    if order:
                        decision['action'] = 'buy'
                        decision['reason'] = f'Strong bullish signal ({probability:.2f} confidence)'
                        decision['order'] = order
                
                # Very strong bearish signal - sell/short (high threshold)
                elif sentiment == "bearish" and probability > 0.85:
                    # Check if we have positions to sell first
                    positions = self.get_positions()
                    long_positions = [p for p in positions if p['symbol'] == self.symbol and p['quantity'] > 0]
                    
                    if long_positions:
                        # Sell existing positions
                        for pos in long_positions:
                            order = self.place_order("sell", abs(pos['quantity']))
                            if order:
                                decision['action'] = 'sell'
                                decision['reason'] = f'Strong bearish signal ({probability:.2f} confidence) - closing positions'
                                decision['order'] = order
            
            return decision
            
        except Exception as e:
            print(f"Error in trading logic: {e}")
            return {
                'timestamp': datetime.now(),
                'error': str(e),
                'action': 'error'
            }
    
    def backtest(self, start_date: str, end_date: str, initial_capital: float = 10000) -> Dict:
        """Simple backtesting functionality"""
        try:
            print(f"🔄 Running backtest for {self.symbol} from {start_date} to {end_date}")
            
            # Get historical data
            data = yf.download(self.symbol, start=start_date, end=end_date)
            if data.empty:
                return {'error': 'No data available for backtest period'}
            
            # Simple buy-and-hold comparison
            start_price = data['Close'].iloc[0]
            end_price = data['Close'].iloc[-1]
            market_return = ((end_price - start_price) / start_price) * 100
            
            # Simulate our strategy (simplified)
            capital = initial_capital
            shares = 0
            trades = []
            
            # Monthly trading simulation
            monthly_data = data.resample('M').last()
            
            for date, row in monthly_data.iterrows():
                price = row['Close']
                
                # Simplified sentiment (using price momentum)
                if len(monthly_data.loc[:date]) >= 2:
                    prev_price = monthly_data.loc[:date]['Close'].iloc[-2]
                    momentum = (price - prev_price) / prev_price
                    
                    # Buy signal
                    if momentum > 0.05 and capital > price:  # 5% monthly gain
                        shares_to_buy = int(capital * 0.5 / price)  # Use 50% of capital
                        if shares_to_buy > 0:
                            cost = shares_to_buy * price
                            capital -= cost
                            shares += shares_to_buy
                            trades.append({'date': date, 'action': 'buy', 'shares': shares_to_buy, 'price': price})
                    
                    # Sell signal
                    elif momentum < -0.08 and shares > 0:  # 8% monthly loss
                        value = shares * price
                        capital += value
                        trades.append({'date': date, 'action': 'sell', 'shares': shares, 'price': price})
                        shares = 0
            
            # Final portfolio value
            final_portfolio_value = capital + (shares * end_price)
            strategy_return = ((final_portfolio_value - initial_capital) / initial_capital) * 100
            
            # Calculate metrics
            returns_series = data['Close'].pct_change().dropna()
            volatility = returns_series.std() * np.sqrt(252) * 100  # Annualized volatility
            max_drawdown = ((data['Close'] / data['Close'].cummax()) - 1).min() * 100
            
            results = {
                'start_date': start_date,
                'end_date': end_date,
                'initial_capital': initial_capital,
                'final_value': round(final_portfolio_value, 2),
                'total_return': f"{strategy_return:+.1f}%",
                'market_return': f"{market_return:+.1f}%",
                'outperformance': f"{strategy_return - market_return:+.1f}%",
                'volatility': f"{volatility:.1f}%",
                'max_drawdown': f"{max_drawdown:.1f}%",
                'total_trades': len(trades),
                'trades': trades[-5:]  # Last 5 trades for display
            }
            
            print(f"✅ Backtest complete: {results['total_return']} vs market {results['market_return']}")
            return results
            
        except Exception as e:
            print(f"❌ Backtest failed: {e}")
            return {'error': str(e)}

# Convenience functions for the web app
def create_trader(symbol: str = "SPY", position_size: float = 0.5) -> LightweightMLTrader:
    """Create a new trader instance"""
    return LightweightMLTrader(symbol=symbol, position_size=position_size)

def run_quick_analysis(symbol: str = "SPY") -> Dict:
    """Quick market analysis for a symbol"""
    trader = create_trader(symbol=symbol)
    
    try:
        current_price = trader.get_current_price()
        probability, sentiment = trader.get_news_sentiment()
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'sentiment': sentiment,
            'probability': probability,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}

# For compatibility with the existing web app
ALPACA_CREDS = {
    "API_KEY": API_KEY,
    "API_SECRET": API_SECRET,
    "PAPER": os.getenv("PAPER", "True").lower() == "true"
}

# Main execution for testing
if __name__ == "__main__":
    print("🚀 Professional Lightweight Trading Bot")
    
    # Test the trader
    trader = create_trader(symbol="SPY", position_size=0.3)
    
    print("\n📊 Current Analysis:")
    analysis = run_quick_analysis("SPY")
    for key, value in analysis.items():
        print(f"  {key}: {value}")
    
    print("\n💰 Account Info:")
    account = trader.get_account_info()
    for key, value in account.items():
        print(f"  {key}: {value}")
        
    print("\n🎯 Current Positions:")
    positions = trader.get_positions()
    if positions:
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['quantity']} shares @ ${pos['avg_entry_price']:.2f}")
    else:
        print("  No current positions")