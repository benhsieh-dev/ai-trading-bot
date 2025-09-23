"""
Schwab Trading Bot Integration
Extends the lightweight trader to support Schwab API for options trading
"""

import os
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional, List, Dict, Any
import time

# Import existing lightweight trader
from tradingbot_lightweight import LightweightMLTrader, API_KEY, API_SECRET
from schwab_api import SchwabAPI, create_schwab_client

# Import database manager for trade persistence
try:
    from database import db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("Database module not available - trades will not be persisted")

class SchwabMLTrader(LightweightMLTrader):
    """Enhanced trading bot with Schwab API support for options trading"""
    
    def __init__(self, symbol: str = "SPY", position_size: float = 0.5, use_schwab: bool = True):
        """Initialize trader with optional Schwab integration
        
        Args:
            symbol: Trading symbol
            position_size: Position sizing
            use_schwab: Whether to use Schwab API for options (falls back to Alpaca for stocks)
        """
        # Initialize parent class (Alpaca integration)
        super().__init__(symbol, position_size)
        
        # Schwab API integration
        self.use_schwab = use_schwab
        self.schwab_client = None
        self.schwab_account_hash = None
        
        if use_schwab:
            self._initialize_schwab()
    
    def _initialize_schwab(self):
        """Initialize Schwab API client"""
        try:
            self.schwab_client = create_schwab_client()
            if self.schwab_client and self.schwab_client._ensure_authenticated():
                # Get account info
                accounts = self.schwab_client.get_account()
                if accounts and len(accounts) > 0:
                    # Use first account (typically the paper trading account)
                    self.schwab_account_hash = accounts[0].get('hashValue')
                    print(f"✅ Schwab API connected - Account: {self.schwab_account_hash[:8]}...")
                else:
                    print("❌ No Schwab accounts found")
                    self.schwab_client = None
            else:
                print("❌ Schwab API authentication failed")
                self.schwab_client = None
        except Exception as e:
            print(f"❌ Schwab API initialization failed: {e}")
            self.schwab_client = None
    
    def is_schwab_available(self) -> bool:
        """Check if Schwab API is available and authenticated"""
        return (self.schwab_client is not None and 
                self.schwab_account_hash is not None and
                self.schwab_client._ensure_authenticated())
    
    def place_option_order(self, symbol: str, option_type: str, strike: float, 
                          expiration: str, side: str, quantity: int) -> Dict[str, Any]:
        """Place an options order using Schwab API
        
        Args:
            symbol: Underlying stock symbol
            option_type: 'call' or 'put'
            strike: Strike price
            expiration: Expiration date (YYYY-MM-DD)
            side: 'buy' or 'sell'
            quantity: Number of contracts
            
        Returns:
            dict: Order result with status and details
        """
        # Try Schwab API first for options
        if self.is_schwab_available():
            try:
                print(f"🎯 Placing option order via Schwab API: {side} {quantity} {symbol} {option_type} ${strike} exp {expiration}")
                
                result = self.schwab_client.place_option_order(
                    account_hash=self.schwab_account_hash,
                    symbol=symbol,
                    option_type=option_type,
                    strike=strike,
                    expiration=expiration,
                    side=side,
                    quantity=quantity
                )
                
                # Format response for consistency
                order_response = {
                    'success': True,
                    'order_id': result.get('order_id'),
                    'status': result.get('status', 'submitted'),
                    'symbol': symbol,
                    'option_symbol': result.get('symbol'),
                    'option_type': option_type,
                    'strike': strike,
                    'expiration': expiration,
                    'side': side,
                    'quantity': quantity,
                    'submitted_at': datetime.now().isoformat(),
                    'broker': 'schwab',
                    'message': f'Schwab {side} order placed for {quantity} {symbol} {option_type} ${strike} exp {expiration}'
                }
                
                # Log to database if available
                if DB_AVAILABLE:
                    try:
                        db_manager.log_trade({
                            'timestamp': datetime.now(),
                            'symbol': symbol,
                            'action': f'option_{side}',
                            'quantity': quantity,
                            'price': strike,  # Will be updated with actual fill price
                            'order_id': result.get('order_id'),
                            'broker': 'schwab',
                            'option_type': option_type,
                            'expiration': expiration,
                            'status': 'submitted'
                        })
                    except Exception as e:
                        print(f"Warning: Could not log trade to database: {e}")
                
                return order_response
                
            except Exception as e:
                print(f"❌ Schwab option order failed: {e}")
                # Fall back to simulation
                return self._simulate_option_order(symbol, option_type, strike, expiration, side, quantity)
        
        # Fall back to simulation if Schwab not available
        print("⚠️  Schwab API not available, using realistic simulation")
        return self._simulate_option_order(symbol, option_type, strike, expiration, side, quantity)
    
    def _simulate_option_order(self, symbol: str, option_type: str, strike: float, 
                              expiration: str, side: str, quantity: int) -> Dict[str, Any]:
        """Simulate option order with realistic pricing (fallback method)"""
        try:
            # Get real current price for realistic simulation
            current_price = self.get_current_price(symbol)
            print(f"Current {symbol} price: ${current_price}")
        except:
            # Fallback price
            current_price = 300
        
        # Simulate realistic option pricing
        days_to_exp = (datetime.strptime(expiration, '%Y-%m-%d') - datetime.now()).days
        
        # Simple Black-Scholes approximation for realistic pricing
        if option_type.lower() == 'call':
            intrinsic = max(0, current_price - strike)
            time_value = max(0.5, (days_to_exp / 30) * strike * 0.02)  # ~2% of strike per month
            option_price = intrinsic + time_value
        else:  # put
            intrinsic = max(0, strike - current_price)
            time_value = max(0.5, (days_to_exp / 30) * strike * 0.02)
            option_price = intrinsic + time_value
        
        # Generate simulated order ID
        mock_order_id = f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}_{strike}{option_type[0].upper()}"
        
        order_response = {
            'success': True,
            'order_id': mock_order_id,
            'status': 'filled',
            'symbol': symbol,
            'option_symbol': f"{symbol}_{expiration.replace('-', '')}_{option_type[0].upper()}{strike}",
            'option_type': option_type,
            'strike': strike,
            'expiration': expiration,
            'side': side,
            'quantity': quantity,
            'submitted_at': datetime.now().isoformat(),
            'simulated_price': round(option_price, 2),
            'total_cost': round(option_price * quantity * 100, 2),
            'broker': 'simulation',
            'message': f'SIMULATED {side} order for {quantity} {symbol} {option_type} ${strike} exp {expiration}',
            'note': 'Realistic simulation using current market data (Schwab API not available)'
        }
        
        # Log simulated trade
        if DB_AVAILABLE:
            try:
                db_manager.log_trade({
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'action': f'option_{side}_sim',
                    'quantity': quantity,
                    'price': option_price,
                    'order_id': mock_order_id,
                    'broker': 'simulation',
                    'option_type': option_type,
                    'expiration': expiration,
                    'status': 'filled'
                })
            except Exception as e:
                print(f"Warning: Could not log simulated trade: {e}")
        
        return order_response
    
    def get_option_chains(self, symbol: str, strike_count: int = 10) -> Optional[Dict[str, Any]]:
        """Get option chains using Schwab API or Yahoo Finance fallback
        
        Args:
            symbol: Stock symbol
            strike_count: Number of strikes to include
            
        Returns:
            dict: Option chains data
        """
        if self.is_schwab_available():
            try:
                return self.schwab_client.get_option_chains(symbol, strike_count)
            except Exception as e:
                print(f"Schwab option chains failed: {e}")
        
        # Fallback to Yahoo Finance (existing implementation)
        try:
            ticker = yf.Ticker(symbol)
            options_dates = ticker.options
            if not options_dates:
                return None
            
            # Get nearest expiration
            nearest_exp = options_dates[0]
            opt = ticker.option_chain(nearest_exp)
            
            return {
                'symbol': symbol,
                'expiration': nearest_exp,
                'calls': opt.calls.to_dict('records'),
                'puts': opt.puts.to_dict('records'),
                'source': 'yahoo_finance'
            }
        except Exception as e:
            print(f"Yahoo Finance option chains failed: {e}")
            return None
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all positions from both Schwab and Alpaca
        
        Returns:
            list: Combined positions from all brokers
        """
        positions = []
        
        # Get Alpaca positions (stocks)
        try:
            alpaca_positions = super().get_positions()
            for pos in alpaca_positions:
                pos['broker'] = 'alpaca'
                positions.append(pos)
        except Exception as e:
            print(f"Error getting Alpaca positions: {e}")
        
        # Get Schwab positions (including options)
        if self.is_schwab_available():
            try:
                schwab_positions = self.schwab_client.get_positions(self.schwab_account_hash)
                for pos in schwab_positions.get('securitiesAccount', {}).get('positions', []):
                    positions.append({
                        'symbol': pos.get('instrument', {}).get('symbol'),
                        'quantity': pos.get('longQuantity', 0) - pos.get('shortQuantity', 0),
                        'market_value': pos.get('marketValue', 0),
                        'asset_type': pos.get('instrument', {}).get('assetType'),
                        'broker': 'schwab'
                    })
            except Exception as e:
                print(f"Error getting Schwab positions: {e}")
        
        return positions
    
    def check_order_status(self, order_id: str, broker: str = 'schwab') -> Optional[Dict[str, Any]]:
        """Check order status
        
        Args:
            order_id: Order ID to check
            broker: Which broker to check ('schwab' or 'alpaca')
            
        Returns:
            dict: Order status information
        """
        if broker == 'schwab' and self.is_schwab_available():
            try:
                return self.schwab_client.get_order(self.schwab_account_hash, order_id)
            except Exception as e:
                print(f"Error checking Schwab order status: {e}")
                return None
        elif broker == 'alpaca':
            try:
                order = self.api.get_order(order_id)
                return {
                    'orderId': order.id,
                    'status': order.status,
                    'symbol': order.symbol,
                    'quantity': order.qty,
                    'side': order.side
                }
            except Exception as e:
                print(f"Error checking Alpaca order status: {e}")
                return None
        
        return None

# Factory function to create the appropriate trader
def create_trader(symbol: str = "SPY", position_size: float = 0.5, use_schwab: bool = True) -> LightweightMLTrader:
    """Create appropriate trader instance
    
    Args:
        symbol: Trading symbol
        position_size: Position sizing
        use_schwab: Whether to attempt Schwab integration
        
    Returns:
        Trader instance (SchwabMLTrader if possible, LightweightMLTrader otherwise)
    """
    # Try to create Schwab-enabled trader
    if use_schwab:
        try:
            schwab_trader = SchwabMLTrader(symbol, position_size, use_schwab=True)
            if schwab_trader.is_schwab_available():
                print("✅ Created Schwab-enabled trader")
                return schwab_trader
            else:
                print("⚠️  Schwab not available, falling back to Alpaca-only trader")
        except Exception as e:
            print(f"⚠️  Schwab trader creation failed: {e}")
    
    # Fall back to original Alpaca-only trader
    return LightweightMLTrader(symbol, position_size)