from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv('MONGODB_URI')
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        if not self.connection_string:
            print("MongoDB URI not configured - running without database persistence")
            self.client = None
            self.db = None
            return
            
        try:
            # Improved connection with timeout settings
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=10000,  # 10 second timeout
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                retryWrites=True,
                w='majority'
            )
            self.db = self.client.trading_bot
            # Test connection
            self.client.admin.command('ping')
            print("MongoDB Atlas connected successfully")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
    
    def is_connected(self):
        return self.client is not None and self.db is not None
    
    def get_portfolio(self, user_id="default"):
        if not self.is_connected():
            return None
        
        portfolio = self.db.portfolios.find_one({"user_id": user_id})
        return portfolio
    
    def update_portfolio(self, user_id, cash, positions):
        if not self.is_connected():
            return False
        
        portfolio_data = {
            "user_id": user_id,
            "cash": cash,
            "positions": positions,
            "last_updated": datetime.utcnow()
        }
        
        self.db.portfolios.replace_one(
            {"user_id": user_id}, 
            portfolio_data, 
            upsert=True
        )
        return True
    
    def save_trade(self, trade_data):
        if not self.is_connected():
            return False
        
        trade_record = {
            "user_id": trade_data.get("user_id", "default"),
            "symbol": trade_data["symbol"],
            "side": trade_data["side"],  # buy/sell
            "quantity": trade_data["quantity"],
            "price": trade_data["price"],
            "timestamp": datetime.utcnow(),
            "strategy": trade_data.get("strategy", "ml_trader"),
            "sentiment": trade_data.get("sentiment"),
            "total_value": trade_data["quantity"] * trade_data["price"]
        }
        
        self.db.trades.insert_one(trade_record)
        return True
    
    def get_trade_history(self, user_id="default", limit=100):
        if not self.is_connected():
            return []
        
        trades = list(self.db.trades.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for trade in trades:
            trade["_id"] = str(trade["_id"])
        
        return trades
    
    def save_backtest_result(self, backtest_data):
        if not self.is_connected():
            return False
        
        backtest_record = {
            "user_id": backtest_data.get("user_id", "default"),
            "symbol": backtest_data["symbol"],
            "start_date": backtest_data["start_date"],
            "end_date": backtest_data["end_date"],
            "position_size": backtest_data["position_size"],
            "results": backtest_data["results"],
            "timestamp": datetime.utcnow()
        }
        
        self.db.backtests.insert_one(backtest_record)
        return True

# Global database instance
db_manager = DatabaseManager()