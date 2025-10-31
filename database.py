import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
from datetime import datetime
import os
import json
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv('DATABASE_URL')
        self.connection = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        if not self.connection_string:
            print("DATABASE_URL not configured - running without database persistence")
            self.connection = None
            return
            
        try:
            self.connection = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor
            )
            self.connection.autocommit = True
            print("PostgreSQL connected successfully")
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
            self.connection = None
    
    def is_connected(self):
        return self.connection is not None
    
    def create_tables(self):
        """Create tables if they don't exist"""
        if not self.is_connected():
            return
        
        try:
            with self.connection.cursor() as cursor:
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(50) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Portfolios table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS portfolios (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        cash DECIMAL(15,2) NOT NULL DEFAULT 0,
                        positions JSONB DEFAULT '[]',
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                """)
                
                # Trades table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trades (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        symbol VARCHAR(10) NOT NULL,
                        side VARCHAR(4) CHECK (side IN ('buy', 'sell')) NOT NULL,
                        quantity INTEGER NOT NULL,
                        price DECIMAL(10,4) NOT NULL,
                        total_value DECIMAL(15,2) NOT NULL,
                        strategy VARCHAR(50) DEFAULT 'ml_trader',
                        sentiment VARCHAR(20),
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                """)
                
                # Backtest results table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backtests (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(50) NOT NULL,
                        symbol VARCHAR(10) NOT NULL,
                        start_date DATE NOT NULL,
                        end_date DATE NOT NULL,
                        position_size DECIMAL(5,4) NOT NULL,
                        results JSONB NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_user_id ON trades(user_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_portfolios_user_id ON portfolios(user_id)")
                
                print("Database tables created successfully")
                
        except Exception as e:
            print(f"Error creating tables: {e}")
    
    def ensure_user_exists(self, user_id="default"):
        """Ensure user exists in database"""
        if not self.is_connected():
            return False
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (user_id) VALUES (%s) ON CONFLICT (user_id) DO NOTHING",
                    (user_id,)
                )
                return True
        except Exception as e:
            print(f"Error ensuring user exists: {e}")
            return False
    
    def get_portfolio(self, user_id="default"):
        if not self.is_connected():
            return None
        
        self.ensure_user_exists(user_id)
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM portfolios WHERE user_id = %s ORDER BY last_updated DESC LIMIT 1",
                    (user_id,)
                )
                portfolio = cursor.fetchone()
                return dict(portfolio) if portfolio else None
        except Exception as e:
            print(f"Error getting portfolio: {e}")
            return None
    
    def update_portfolio(self, user_id, cash, positions):
        if not self.is_connected():
            return False
        
        self.ensure_user_exists(user_id)
        
        try:
            with self.connection.cursor() as cursor:
                # Convert positions to JSON string
                positions_json = json.dumps(positions)
                
                cursor.execute("""
                    INSERT INTO portfolios (user_id, cash, positions, last_updated)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        cash = EXCLUDED.cash,
                        positions = EXCLUDED.positions,
                        last_updated = EXCLUDED.last_updated
                """, (user_id, cash, positions_json, datetime.utcnow()))
                
                return True
        except Exception as e:
            print(f"Database update_portfolio error: {e}")
            return False
    
    def save_trade(self, trade_data):
        if not self.is_connected():
            return False
        
        user_id = trade_data.get("user_id", "default")
        self.ensure_user_exists(user_id)
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO trades (user_id, symbol, side, quantity, price, total_value, strategy, sentiment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    trade_data["symbol"],
                    trade_data["side"],
                    trade_data["quantity"],
                    trade_data["price"],
                    trade_data["quantity"] * trade_data["price"],
                    trade_data.get("strategy", "ml_trader"),
                    trade_data.get("sentiment")
                ))
                return True
        except Exception as e:
            print(f"Database save_trade error: {e}")
            return False
    
    def get_trade_history(self, user_id="default", limit=100):
        if not self.is_connected():
            return []
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM trades 
                    WHERE user_id = %s 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """, (user_id, limit))
                
                trades = cursor.fetchall()
                return [dict(trade) for trade in trades]
        except Exception as e:
            print(f"Error getting trade history: {e}")
            return []
    
    def save_backtest_result(self, backtest_data):
        if not self.is_connected():
            return False
        
        user_id = backtest_data.get("user_id", "default")
        self.ensure_user_exists(user_id)
        
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO backtests (user_id, symbol, start_date, end_date, position_size, results)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    user_id,
                    backtest_data["symbol"],
                    backtest_data["start_date"],
                    backtest_data["end_date"],
                    backtest_data["position_size"],
                    json.dumps(backtest_data["results"])
                ))
                return True
        except Exception as e:
            print(f"Database save_backtest_result error: {e}")
            return False
    
    def get_portfolio_stats(self, user_id="default"):
        """Get portfolio statistics"""
        if not self.is_connected():
            return {}
        
        try:
            with self.connection.cursor() as cursor:
                # Get total trades
                cursor.execute("SELECT COUNT(*) as total_trades FROM trades WHERE user_id = %s", (user_id,))
                total_trades = cursor.fetchone()['total_trades']
                
                # Get total volume
                cursor.execute("SELECT SUM(total_value) as total_volume FROM trades WHERE user_id = %s", (user_id,))
                total_volume = cursor.fetchone()['total_volume'] or 0
                
                # Get buy/sell counts
                cursor.execute("""
                    SELECT side, COUNT(*) as count 
                    FROM trades 
                    WHERE user_id = %s 
                    GROUP BY side
                """, (user_id,))
                side_counts = {row['side']: row['count'] for row in cursor.fetchall()}
                
                return {
                    'total_trades': total_trades,
                    'total_volume': float(total_volume),
                    'buy_orders': side_counts.get('buy', 0),
                    'sell_orders': side_counts.get('sell', 0)
                }
        except Exception as e:
            print(f"Error getting portfolio stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("PostgreSQL connection closed")

# Global database instance
db_manager = DatabaseManager()