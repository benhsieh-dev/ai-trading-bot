#!/usr/bin/env python3
"""
Debug script to check Alpaca positions directly
"""

import os
from dotenv import load_dotenv
from alpaca_trade_api import REST

load_dotenv()

# Get API credentials
API_KEY = os.getenv("ALPACA_API_KEY")  
API_SECRET = os.getenv("ALPACA_API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

print("=== Alpaca Debug Info ===")
print(f"API Key: {API_KEY[:10]}..." if API_KEY else "No API Key")
print(f"Base URL: {BASE_URL}")

if not API_KEY or not API_SECRET:
    print("❌ Missing API credentials")
    exit(1)

try:
    # Initialize API
    api = REST(
        key_id=API_KEY,
        secret_key=API_SECRET,
        base_url=BASE_URL,
        api_version='v2'
    )
    
    print("\n=== Account Info ===")
    account = api.get_account()
    print(f"Cash: ${float(account.cash):,.2f}")
    print(f"Portfolio Value: ${float(account.portfolio_value):,.2f}")
    print(f"Buying Power: ${float(account.buying_power):,.2f}")
    
    print("\n=== Positions ===")
    positions = api.list_positions()
    print(f"Found {len(positions)} positions:")
    
    for pos in positions:
        print(f"  • {pos.symbol}: {pos.qty} shares @ ${float(pos.avg_entry_price):.2f}")
        print(f"    Market Value: ${float(pos.market_value):.2f}")
        print(f"    P&L: ${float(pos.unrealized_pl):.2f} ({float(pos.unrealized_plpc)*100:.2f}%)")
    
    print("\n=== Recent Orders ===")
    orders = api.list_orders(status='all', limit=10)
    print(f"Found {len(orders)} recent orders:")
    
    for order in orders:
        print(f"  • {order.side.upper()} {order.qty} {order.symbol}")
        print(f"    Status: {order.status}")
        print(f"    Submitted: {order.submitted_at}")
        print(f"    Filled: {order.filled_at if order.filled_at else 'Not filled'}")
        print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()