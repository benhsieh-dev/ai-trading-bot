#!/usr/bin/env python3
"""
Schwab API Setup and Authentication Script
Run this script to authenticate with Schwab API for options trading
"""

import os
import sys
from dotenv import load_dotenv
from schwab_api import authenticate_schwab

def main():
    """Setup Schwab API authentication"""
    print("🚀 Schwab API Setup for AI Trading Bot")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if credentials are configured
    client_id = os.getenv("SCHWAB_CLIENT_ID")
    client_secret = os.getenv("SCHWAB_CLIENT_SECRET")
    
    if not client_id or client_id == "your_schwab_client_id_here":
        print("❌ Schwab API credentials not configured!")
        print("\n📋 Setup Instructions:")
        print("1. Go to https://developer.schwab.com/")
        print("2. Create a developer account (separate from brokerage account)")
        print("3. Create a new application:")
        print("   - Application Type: 'Individual'")
        print("   - Description: 'Personal trading automation'")
        print("   - Redirect URL: https://127.0.0.1")
        print("4. Request access to 'Accounts and Trading Production' + 'Market Data Production'")
        print("5. Wait for approval (usually 1-3 business days)")
        print("6. Update .env file with your credentials:")
        print("   SCHWAB_CLIENT_ID=your_actual_client_id")
        print("   SCHWAB_CLIENT_SECRET=your_actual_client_secret")
        print("\n⚠️  Keep your application description simple to get approved faster!")
        return False
    
    print(f"✅ Schwab credentials found")
    print(f"Client ID: {client_id[:8]}...")
    
    # Attempt authentication
    print("\n🔐 Starting authentication flow...")
    client = authenticate_schwab()
    
    if client:
        print("✅ Schwab API authentication successful!")
        print("📊 Testing API connection...")
        
        try:
            # Test API connection
            accounts = client.get_account()
            print(f"✅ Connected to {len(accounts)} Schwab account(s)")
            
            if accounts:
                account = accounts[0]
                account_hash = account.get('hashValue', 'unknown')
                account_type = account.get('type', 'unknown')
                print(f"   Account: {account_hash[:8]}... ({account_type})")
                
                # Check if it's a paper trading account
                if 'paper' in account_type.lower() or 'sim' in account_type.lower():
                    print("🎯 Paper trading account detected - perfect for options testing!")
                else:
                    print("⚠️  Live account detected - make sure you want to use this for trading")
            
            print("\n🎉 Setup complete! Your bot can now trade options through Schwab API.")
            print("📝 Your authentication tokens have been saved to .schwab_tokens.json")
            return True
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
    
    else:
        print("❌ Authentication failed")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure your Schwab application is approved")
        print("2. Check that your client ID and secret are correct")
        print("3. Ensure the redirect URI matches exactly: https://127.0.0.1")
        print("4. Try the authentication flow again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)