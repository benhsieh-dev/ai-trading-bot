from flask import Flask, render_template, jsonify, request
import threading
from datetime import datetime
import json
import os
from database import db_manager
import random
import requests

app = Flask(__name__)

# Mock trading bot functionality for Render deployment
class MockMLTrader:
    def __init__(self, name, parameters):
        self.name = name
        self.parameters = parameters
        self.cash = 10000.0
        self.positions = []
        
    def initialize(self, symbol, position_size):
        self.symbol = symbol
        self.position_size = position_size
        
    def get_sentiment(self):
        # Mock sentiment analysis
        sentiments = ['bullish', 'bearish', 'neutral']
        sentiment = random.choice(sentiments)
        probability = random.uniform(0.4, 0.9)
        return probability, sentiment
        
    def get_cash(self):
        return self.cash
        
    def get_positions(self):
        return []
        
    def get_last_price(self, symbol):
        # Mock prices for common symbols
        mock_prices = {
            'SPY': 430 + random.uniform(-5, 5),
            'NVDA': 120 + random.uniform(-10, 10),
            'AAPL': 185 + random.uniform(-8, 8),
            'MSFT': 340 + random.uniform(-15, 15),
        }
        return mock_prices.get(symbol, 100 + random.uniform(-10, 10))

def generate_realistic_results(symbol, start_year, end_year, position_size):
    """Generate realistic backtest results based on market conditions"""
    
    market_scenarios = {
        2020: {'market_return': '+16.3%', 'volatility': 'high', 'ai_advantage': 0.85, 'sentiment_accuracy': 0.78},
        2021: {'market_return': '+26.9%', 'volatility': 'low', 'ai_advantage': 0.95, 'sentiment_accuracy': 0.65},
        2022: {'market_return': '-18.1%', 'volatility': 'high', 'ai_advantage': 1.25, 'sentiment_accuracy': 0.82},
        2023: {'market_return': '+24.2%', 'volatility': 'medium', 'ai_advantage': 1.1, 'sentiment_accuracy': 0.73},
        2024: {'market_return': '+12.5%', 'volatility': 'medium', 'ai_advantage': 1.05, 'sentiment_accuracy': 0.71}
    }
    
    scenario = market_scenarios.get(start_year, {
        'market_return': '+8.0%', 'volatility': 'medium', 'ai_advantage': 1.0, 'sentiment_accuracy': 0.70
    })
    
    market_return_float = float(scenario['market_return'].replace('%', '').replace('+', ''))
    ai_return = market_return_float * scenario['ai_advantage'] + random.uniform(-3, 3)
    
    if scenario['volatility'] == 'high':
        max_drawdown = random.uniform(-15, -25)
        sharpe_ratio = random.uniform(0.8, 1.4)
        total_trades = random.randint(45, 85)
    elif scenario['volatility'] == 'low':
        max_drawdown = random.uniform(-5, -12)
        sharpe_ratio = random.uniform(1.2, 2.1)
        total_trades = random.randint(15, 35)
    else:
        max_drawdown = random.uniform(-8, -18)
        sharpe_ratio = random.uniform(1.0, 1.8)
        total_trades = random.randint(25, 55)
    
    win_rate = (scenario['sentiment_accuracy'] * 100) + random.uniform(-8, 8)
    win_rate = max(45, min(85, win_rate))
    avg_trade = ai_return / total_trades if total_trades > 0 else 0
    
    return {
        'total_return': f"{ai_return:+.1f}%",
        'sharpe_ratio': f"{sharpe_ratio:.2f}",
        'max_drawdown': f"{max_drawdown:.1f}%",
        'total_trades': str(total_trades),
        'win_rate': f"{win_rate:.1f}%",
        'avg_trade': f"{avg_trade:+.2f}%",
        'market_return': scenario['market_return'],
        'volatility': scenario['volatility'],
        'sentiment_accuracy': f"{scenario['sentiment_accuracy']*100:.1f}%"
    }

# Global variables for mock bot state
bot_running = False
current_strategy = None
trading_data = {
    'status': 'stopped',
    'last_sentiment': None,
    'last_probability': None,
    'last_trade': None,
    'cash': 10000,
    'positions': [],
    'trades_today': 0
}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/status')
def get_status():
    return jsonify(trading_data)

@app.route('/api/start', methods=['POST'])
def start_trading():
    global bot_running, current_strategy, trading_data
    
    if bot_running:
        return jsonify({'error': 'Bot is already running'}), 400
    
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'SPY')
        position_size = float(data.get('position_size', 0.5))
        
        # Create mock strategy for demo
        current_strategy = MockMLTrader(
            name='mlstrat', 
            parameters={"symbol": symbol, "position_size": position_size}
        )
        current_strategy.initialize(symbol=symbol, position_size=position_size)
        
        bot_running = True
        trading_data['status'] = 'running'
        
        return jsonify({'message': 'Trading bot initialized successfully (demo mode on Render)'})
    
    except Exception as e:
        return jsonify({'error': f'Failed to start bot: {str(e)}'}), 500

@app.route('/api/stop', methods=['POST'])
def stop_trading():
    global bot_running, trading_data
    
    if not bot_running:
        return jsonify({'error': 'Bot is not running'}), 400
    
    try:
        bot_running = False
        trading_data['status'] = 'stopped'
        return jsonify({'message': 'Trading bot stopped successfully'})
    
    except Exception as e:
        return jsonify({'error': f'Failed to stop bot: {str(e)}'}), 500

@app.route('/api/sentiment')
def get_sentiment():
    if current_strategy and bot_running:
        try:
            probability, sentiment = current_strategy.get_sentiment()
            trading_data['last_sentiment'] = sentiment
            trading_data['last_probability'] = float(probability)
            
            return jsonify({
                'sentiment': sentiment,
                'probability': float(probability),
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            return jsonify({'error': f'Failed to get sentiment: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Bot not running'}), 400

@app.route('/api/portfolio')
def get_portfolio():
    user_id = "default"
    
    if current_strategy and bot_running:
        try:
            cash = current_strategy.get_cash()
            positions = []  # Mock empty positions for demo
            
            if db_manager.is_connected():
                db_manager.update_portfolio(user_id, cash, positions)
            
            trading_data['cash'] = cash
            trading_data['positions'] = positions
            
            return jsonify({
                'cash': round(cash, 2),
                'positions': positions
            })
        except Exception as e:
            return jsonify({'error': f'Failed to get portfolio: {str(e)}'}), 500
    else:
        # Try database fallback
        if db_manager.is_connected():
            db_portfolio = db_manager.get_portfolio(user_id)
            if db_portfolio:
                return jsonify({
                    'cash': db_portfolio.get('cash', 10000),
                    'positions': db_portfolio.get('positions', [])
                })
        
        return jsonify({
            'cash': 10000,
            'positions': []
        })

@app.route('/api/backtest', methods=['POST'])
def run_backtest():
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'SPY')
        position_size = float(data.get('position_size', 0.5))
        start_year = int(data.get('start_year', 2023))
        end_year = int(data.get('end_year', 2023))
        
        # Generate realistic results
        mock_results = generate_realistic_results(symbol, start_year, end_year, position_size)
        
        return jsonify({
            'status': 'completed',
            'symbol': symbol,
            'start_date': f'{start_year}-01-01',
            'end_date': f'{end_year}-12-31',
            'position_size': position_size,
            'results': mock_results,
            'output': f'Backtest completed successfully for {symbol}',
            'message': f'Demo backtest completed for {symbol} from {start_year} to {end_year}',
            'note': 'This is a demo version running on Render with realistic mock data'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to start backtest: {str(e)}'}), 500

@app.route('/api/options/<symbol>')
def get_options_chain(symbol):
    """Mock options chain for demo"""
    try:
        # Mock current prices
        symbol_prices = {
            'SPY': 430, 'NVDA': 120, 'AAPL': 185, 'MSFT': 340,
            'GOOGL': 140, 'TSLA': 250, 'META': 320, 'AMZN': 150,
            'AMD': 140, 'QQQ': 360, 'IWM': 200, 'GLD': 180
        }
        current_price = symbol_prices.get(symbol.upper(), 100)
        
        strikes = []
        strike_spacing = 10 if current_price > 200 else (5 if current_price > 100 else 2.5)
        
        for i in range(-10, 11):
            strike = round((current_price + (i * strike_spacing)) * 2) / 2
            time_value = 3 + (2 * abs(i) / 10)
            
            call_price = max(0.01, max(0, current_price - strike) + time_value)
            put_price = max(0.01, max(0, strike - current_price) + time_value)
            
            strikes.append({
                'strike': strike,
                'call': {'bid': call_price * 0.95, 'ask': call_price * 1.05, 'last': call_price},
                'put': {'bid': put_price * 0.95, 'ask': put_price * 1.05, 'last': put_price}
            })
        
        return jsonify({
            'symbol': symbol.upper(),
            'current_price': current_price,
            'strikes': strikes,
            'data_source': 'demo_mock',
            'note': 'Demo version with realistic mock options data'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch options data: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)