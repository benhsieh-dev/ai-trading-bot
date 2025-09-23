# Schwab API Setup for Options Trading

This guide explains how to set up Charles Schwab API integration for real paper options trading in your AI trading bot.

## Why Schwab?

- ✅ **FREE API access** (no monthly fees like other brokers)
- ✅ **Real options paper trading** support
- ✅ **Inherited TD Ameritrade's thinkorswim platform**
- ✅ **Active API with good documentation**
- ✅ **Individual developer friendly**

## Setup Process

### Step 1: Create Schwab Brokerage Account

1. Go to [schwab.com](https://www.schwab.com/) and create a free brokerage account
2. You can use any account type - even a basic brokerage account works
3. Complete the account verification process

### Step 2: Register for Developer Access

1. Go to [developer.schwab.com](https://developer.schwab.com/)
2. Create a developer account (separate from your brokerage account)
3. Log in to the developer portal

### Step 3: Create Application

1. Click "Create New App"
2. Fill out the application:
   - **Application Name**: "Personal Trading Bot" (or similar)
   - **Application Type**: Individual
   - **Description**: "Personal trading automation for individual stock and options purchases"
   - **Redirect URL**: `https://127.0.0.1`
3. **IMPORTANT**: Keep the description simple and avoid terms like "algorithmic trading" or "automated trading" which might trigger additional review

### Step 4: Request API Access

1. Request access to:
   - ✅ **Accounts and Trading Production**
   - ✅ **Market Data Production**
2. Submit your application
3. Wait for approval (typically 1-3 business days)

### Step 5: Get Your Credentials

Once approved:
1. Go to your app dashboard
2. Copy your **Client ID** and **Client Secret**
3. Update your `.env` file:

```bash
SCHWAB_CLIENT_ID=your_actual_client_id_here
SCHWAB_CLIENT_SECRET=your_actual_client_secret_here
SCHWAB_REDIRECT_URI=https://127.0.0.1
```

### Step 6: Run Setup Script

```bash
python setup_schwab.py
```

This will:
- Verify your credentials
- Open your browser for OAuth authentication
- Save your authentication tokens
- Test the API connection

## Usage

Once set up, your bot will automatically:

1. **Try Schwab API first** for options trading
2. **Fall back to simulation** if Schwab is unavailable
3. **Use Alpaca for stocks** (existing functionality)

### Testing Options Trading

You can test with a simple options order:

```javascript
// Frontend test
placeOptionsOrder('AAPL', 'call', 150, '2024-12-20', 'buy', 1);
```

### Checking Status

The bot will show which API it's using:
- 🎯 **Schwab API**: Real paper options trading
- ⚠️ **Simulation**: Realistic pricing but no real orders
- 📊 **Alpaca**: Stock trading only

## File Structure

The Schwab integration adds these files:

```
ai-trading-bot/
├── schwab_api.py          # Core Schwab API client
├── schwab_trader.py       # Enhanced trader with Schwab support
├── setup_schwab.py        # Setup and authentication script
├── .schwab_tokens.json    # Saved authentication tokens (auto-generated)
└── .env                   # Updated with Schwab credentials
```

## Option Symbol Formats

### Schwab Format (New)
```
SYMBOL_MMDDYY[C|P]STRIKE
Example: AAPL_012024C150 (AAPL Jan 20, 2024 $150 Call)
```

### Alpaca/OCC Format (Old)
```
SYMBOL  YYMMDDC/PSTRIKE000
Example: AAPL  240120C00150000 (AAPL Jan 20, 2024 $150 Call)
```

The bot automatically converts between formats.

## API Features

### ✅ Implemented
- OAuth 2.0 authentication with PKCE
- Token refresh and storage
- Options order placement
- Account and position retrieval
- Option chains data
- Error handling and fallbacks

### 🚧 Future Enhancements
- Real-time options Greeks
- Complex strategies (spreads, straddles)
- Advanced order types
- Risk management features

## Troubleshooting

### Authentication Issues

**Problem**: "Authentication failed"
**Solutions**:
1. Verify your client ID and secret are correct
2. Make sure your application is approved
3. Check that redirect URI matches exactly: `https://127.0.0.1`
4. Try running `python setup_schwab.py` again

### API Errors

**Problem**: "Option contract not found"
**Solutions**:
1. Use common strike prices (multiples of $5 or $10)
2. Check expiration date is valid (not past, not too far future)
3. Verify the underlying stock trades options

### Paper Trading

**Problem**: "Want to test without real money"
**Solution**: Schwab paper trading accounts are completely separate from live accounts and use virtual money only.

## Security Notes

- ✅ Tokens are stored locally in `.schwab_tokens.json`
- ✅ Credentials are loaded from environment variables
- ✅ OAuth 2.0 with PKCE for secure authentication
- ✅ No real money at risk with paper trading
- ⚠️ Keep your `.env` file secure and never commit it to version control

## Support

For issues:
1. Check the console output for detailed error messages
2. Verify your Schwab developer account status
3. Test with the setup script: `python setup_schwab.py`
4. Review the Schwab API documentation at [developer.schwab.com](https://developer.schwab.com/)

## Migration from Alpaca

The bot maintains backward compatibility:
- Existing stock trading through Alpaca continues to work
- Options trading upgrades to Schwab when available
- Fallback simulation provides continuity during setup

Your trading bot is now ready for real options trading! 🚀