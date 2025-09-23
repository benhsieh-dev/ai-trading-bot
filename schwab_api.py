"""
Schwab API Client for Paper Options Trading
Implements OAuth 2.0 authentication and options trading functionality
"""

import os
import json
import time
import base64
import hashlib
import secrets
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from urllib.parse import urlencode, parse_qs, urlparse
import webbrowser

class SchwabAPI:
    """Schwab API client with OAuth 2.0 authentication and options trading support"""
    
    def __init__(self, client_id: str = None, client_secret: str = None, redirect_uri: str = "https://127.0.0.1"):
        """Initialize Schwab API client
        
        Args:
            client_id: Schwab application client ID
            client_secret: Schwab application client secret  
            redirect_uri: OAuth redirect URI (must match registered URI)
        """
        self.client_id = client_id or os.getenv("SCHWAB_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SCHWAB_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("SCHWAB_REDIRECT_URI", "https://127.0.0.1")
        
        # Schwab API endpoints
        self.auth_url = "https://api.schwabapi.com/oauth/authorize"
        self.token_url = "https://api.schwabapi.com/oauth/token"
        self.base_url = "https://api.schwabapi.com"
        
        # Authentication state
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # Load saved tokens if available
        self._load_tokens()
    
    def _load_tokens(self):
        """Load saved tokens from file"""
        try:
            with open('.schwab_tokens.json', 'r') as f:
                data = json.load(f)
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
                expires_str = data.get('expires_at')
                if expires_str:
                    self.token_expires_at = datetime.fromisoformat(expires_str)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    def _save_tokens(self):
        """Save tokens to file"""
        data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
        }
        with open('.schwab_tokens.json', 'w') as f:
            json.dump(data, f)
    
    def get_authorization_url(self) -> tuple[str, str]:
        """Generate authorization URL for OAuth 2.0 flow
        
        Returns:
            tuple: (authorization_url, state) for PKCE verification
        """
        # Generate PKCE challenge
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        
        # Store for later verification
        self.code_verifier = code_verifier
        self.oauth_state = state
        
        # Build authorization URL
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'api',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        return auth_url, state
    
    def authenticate_interactive(self) -> bool:
        """Interactive authentication flow - opens browser for user consent
        
        Returns:
            bool: True if authentication successful
        """
        print("Starting Schwab API authentication...")
        
        # Get authorization URL
        auth_url, state = self.get_authorization_url()
        
        # Open browser for user authentication
        print(f"Opening browser for authentication: {auth_url}")
        webbrowser.open(auth_url)
        
        # Get authorization code from user
        print("\nAfter authorizing the application, you'll be redirected to a URL.")
        print("Copy the entire URL and paste it here:")
        callback_url = input("Callback URL: ").strip()
        
        # Parse the callback URL
        parsed = urlparse(callback_url)
        query_params = parse_qs(parsed.query)
        
        # Verify state
        returned_state = query_params.get('state', [None])[0]
        if returned_state != state:
            print("ERROR: State mismatch - possible CSRF attack")
            return False
        
        # Get authorization code
        auth_code = query_params.get('code', [None])[0]
        if not auth_code:
            error = query_params.get('error', [None])[0]
            print(f"ERROR: Authorization failed: {error}")
            return False
        
        # Exchange code for tokens
        return self._exchange_code_for_tokens(auth_code)
    
    def _exchange_code_for_tokens(self, auth_code: str) -> bool:
        """Exchange authorization code for access/refresh tokens
        
        Args:
            auth_code: Authorization code from OAuth callback
            
        Returns:
            bool: True if token exchange successful
        """
        # Prepare token request
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'code_verifier': self.code_verifier,
            'client_id': self.client_id
        }
        
        # Prepare headers with client credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {b64_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Store tokens
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token')
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Save tokens
            self._save_tokens()
            
            print("✅ Authentication successful!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Token exchange failed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return False
    
    def _refresh_access_token(self) -> bool:
        """Refresh access token using refresh token
        
        Returns:
            bool: True if refresh successful
        """
        if not self.refresh_token:
            return False
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id
        }
        
        credentials = f"{self.client_id}:{self.client_secret}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {b64_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = requests.post(self.token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
            
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            self._save_tokens()
            return True
            
        except requests.exceptions.RequestException:
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid access token
        
        Returns:
            bool: True if we have a valid token
        """
        # Check if we have a token and it's not expired
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at - timedelta(minutes=5):
                return True
        
        # Try to refresh token
        if self.refresh_token:
            if self._refresh_access_token():
                return True
        
        # Need new authentication
        print("No valid tokens available. Please authenticate.")
        return False
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated API request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional request parameters
            
        Returns:
            requests.Response: API response
        """
        if not self._ensure_authenticated():
            raise Exception("Authentication required")
        
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        headers['Accept'] = 'application/json'
        kwargs['headers'] = headers
        
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, **kwargs)
        
        # Handle token expiration
        if response.status_code == 401:
            if self._refresh_access_token():
                headers['Authorization'] = f'Bearer {self.access_token}'
                response = requests.request(method, url, **kwargs)
        
        return response
    
    def get_account(self) -> Dict[str, Any]:
        """Get account information
        
        Returns:
            dict: Account details
        """
        response = self._make_request('GET', '/trader/v1/accounts')
        response.raise_for_status()
        return response.json()
    
    def get_positions(self, account_hash: str) -> Dict[str, Any]:
        """Get account positions
        
        Args:
            account_hash: Account hash from get_account()
            
        Returns:
            dict: Positions data
        """
        endpoint = f'/trader/v1/accounts/{account_hash}/positions'
        response = self._make_request('GET', endpoint)
        response.raise_for_status()
        return response.json()
    
    def get_option_chains(self, symbol: str, strike_count: int = 10) -> Dict[str, Any]:
        """Get option chains for a symbol
        
        Args:
            symbol: Stock symbol
            strike_count: Number of strikes to return
            
        Returns:
            dict: Option chains data
        """
        params = {
            'symbol': symbol,
            'strikeCount': strike_count,
            'strategy': 'SINGLE'
        }
        
        response = self._make_request('GET', '/marketdata/v1/chains', params=params)
        response.raise_for_status()
        return response.json()
    
    def format_option_symbol(self, symbol: str, expiration: str, option_type: str, strike: float) -> str:
        """Format option symbol for Schwab API
        
        Args:
            symbol: Underlying stock symbol
            expiration: Expiration date (YYYY-MM-DD)
            option_type: 'call' or 'put'
            strike: Strike price
            
        Returns:
            str: Formatted option symbol for Schwab
        """
        # Schwab uses a different format than Alpaca's OCC format
        # Format: SYMBOL_MMDDYY(C|P)STRIKE
        # Example: AAPL_012024C150
        
        exp_date = datetime.strptime(expiration, '%Y-%m-%d')
        exp_str = exp_date.strftime('%m%d%y')
        option_side = 'C' if option_type.lower() == 'call' else 'P'
        
        # Format strike without decimal if it's a whole number
        if strike == int(strike):
            strike_str = str(int(strike))
        else:
            strike_str = f"{strike:.2f}".replace('.', '')
        
        return f"{symbol}_{exp_str}{option_side}{strike_str}"
    
    def place_option_order(self, account_hash: str, symbol: str, option_type: str, 
                          strike: float, expiration: str, side: str, quantity: int) -> Dict[str, Any]:
        """Place an options order
        
        Args:
            account_hash: Account hash from get_account()
            symbol: Underlying stock symbol
            option_type: 'call' or 'put'
            strike: Strike price
            expiration: Expiration date (YYYY-MM-DD)
            side: 'buy' or 'sell'
            quantity: Number of contracts
            
        Returns:
            dict: Order response
        """
        option_symbol = self.format_option_symbol(symbol, expiration, option_type, strike)
        
        # Build order payload
        order_data = {
            "orderType": "MARKET",
            "session": "NORMAL",
            "duration": "DAY",
            "orderStrategyType": "SINGLE",
            "orderLegCollection": [
                {
                    "instruction": "BUY_TO_OPEN" if side.lower() == "buy" else "SELL_TO_OPEN",
                    "quantity": quantity,
                    "instrument": {
                        "symbol": option_symbol,
                        "assetType": "OPTION"
                    }
                }
            ]
        }
        
        endpoint = f'/trader/v1/accounts/{account_hash}/orders'
        response = self._make_request('POST', endpoint, json=order_data)
        response.raise_for_status()
        
        # Get order ID from Location header
        location = response.headers.get('Location', '')
        order_id = location.split('/')[-1] if location else None
        
        return {
            'order_id': order_id,
            'status': 'submitted',
            'symbol': option_symbol,
            'quantity': quantity,
            'side': side
        }
    
    def get_order(self, account_hash: str, order_id: str) -> Dict[str, Any]:
        """Get order details
        
        Args:
            account_hash: Account hash
            order_id: Order ID
            
        Returns:
            dict: Order details
        """
        endpoint = f'/trader/v1/accounts/{account_hash}/orders/{order_id}'
        response = self._make_request('GET', endpoint)
        response.raise_for_status()
        return response.json()

# Convenience functions for backward compatibility
def create_schwab_client() -> Optional[SchwabAPI]:
    """Create Schwab API client if credentials are available
    
    Returns:
        SchwabAPI client or None if credentials missing
    """
    client_id = os.getenv("SCHWAB_CLIENT_ID")
    client_secret = os.getenv("SCHWAB_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Schwab API credentials not found in environment variables")
        print("Please set SCHWAB_CLIENT_ID and SCHWAB_CLIENT_SECRET")
        return None
    
    return SchwabAPI(client_id, client_secret)

def authenticate_schwab() -> Optional[SchwabAPI]:
    """Interactive Schwab authentication
    
    Returns:
        Authenticated SchwabAPI client or None
    """
    client = create_schwab_client()
    if not client:
        return None
    
    if client.authenticate_interactive():
        return client
    
    return None