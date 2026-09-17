import { useEffect, useState } from 'react';
import { tradingApi } from '../../api/tradingApi';
import './TradeHistory.css';

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value ?? 0);
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString();
}

function getBuyOrdersCount(trades: any[]): number {
  return trades.filter((trade) => trade.side === 'buy').length;
}

function getSellOrdersCount(trades: any[]): number {
  return trades.filter((trade) => trade.side === 'sell').length;
}

function getTotalVolume(trades: any[]): number {
  return trades.reduce((total, trade) => total + (trade.total_value || 0), 0);
}

function TradeHistory() {
  const [tradeHistory, setTradeHistory] = useState<any>(null);
  const [portfolioHistory, setPortfolioHistory] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const loadTradeHistory = () => {
    tradingApi.getTradeHistory().then(setTradeHistory).catch(() => {});
  };

  const loadPortfolioHistory = () => {
    tradingApi.getPortfolioHistory().then(setPortfolioHistory).catch(() => {});
  };

  useEffect(() => {
    loadTradeHistory();
    loadPortfolioHistory();
    const interval = setInterval(() => {
      loadTradeHistory();
      loadPortfolioHistory();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const refreshData = () => {
    setIsLoading(true);
    loadTradeHistory();
    loadPortfolioHistory();
    setTimeout(() => setIsLoading(false), 1000);
  };

  return (
    <div className="trade-history-container">
      <div className="th-header">
        <h2>Trade History (PostgreSQL)</h2>
        <button className="refresh-btn" onClick={refreshData} disabled={isLoading}>
          {isLoading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      <div className="th-section">
        <h3>Recent Trades</h3>

        {tradeHistory && (
          <div>
            {tradeHistory.source === 'postgresql' && (
              <div className="database-status database-connected">
                ✅ Connected to PostgreSQL
                <span className="th-muted">({tradeHistory.count} trades found)</span>
              </div>
            )}

            {tradeHistory.source === 'no_database' && (
              <div className="database-status database-disconnected">
                ❌ Database not connected
                <p className="th-muted">{tradeHistory.message}</p>
              </div>
            )}

            {tradeHistory.trades && tradeHistory.trades.length > 0 && (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Symbol</th>
                      <th>Side</th>
                      <th className="th-right">Quantity</th>
                      <th className="th-right">Price</th>
                      <th className="th-right">Total Value</th>
                      <th>Strategy</th>
                      <th>Sentiment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tradeHistory.trades.map((trade: any, i: number) => (
                      <tr key={i}>
                        <td>{formatDate(trade.timestamp)}</td>
                        <td className="th-strong">{trade.symbol}</td>
                        <td>
                          <span className={trade.side === 'buy' ? 'th-buy' : 'th-sell'}>{trade.side}</span>
                        </td>
                        <td className="th-right">{trade.quantity}</td>
                        <td className="th-right">{formatCurrency(trade.price)}</td>
                        <td className="th-right th-strong">{formatCurrency(trade.total_value)}</td>
                        <td>{trade.strategy || 'N/A'}</td>
                        <td>{trade.sentiment || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {tradeHistory.trades && tradeHistory.trades.length === 0 && (
              <div className="th-empty">
                <p>No trades found in database</p>
                <p className="th-muted">Execute some trades to see history here</p>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="th-section">
        <h3>Portfolio Overview</h3>

        {portfolioHistory && (
          <div>
            {portfolioHistory.source === 'mongodb' && (
              <div className="th-grid">
                <div className="th-card">
                  <h4>Current Portfolio</h4>
                  {portfolioHistory.current_portfolio ? (
                    <div>
                      <p><strong>Cash:</strong> {formatCurrency(portfolioHistory.current_portfolio.cash)}</p>
                      <p><strong>Last Updated:</strong> {formatDate(portfolioHistory.current_portfolio.last_updated)}</p>
                      <p><strong>Positions:</strong> {portfolioHistory.current_portfolio.positions?.length ?? 0}</p>
                    </div>
                  ) : (
                    <div className="th-muted">No portfolio data in database yet</div>
                  )}
                </div>

                <div className="th-card">
                  <h4>Trade Statistics</h4>
                  {portfolioHistory.recent_trades && portfolioHistory.recent_trades.length > 0 ? (
                    <div>
                      <p><strong>Total Trades:</strong> {portfolioHistory.recent_trades.length}</p>
                      <p><strong>Buy Orders:</strong> {getBuyOrdersCount(portfolioHistory.recent_trades)}</p>
                      <p><strong>Sell Orders:</strong> {getSellOrdersCount(portfolioHistory.recent_trades)}</p>
                      <p><strong>Total Volume:</strong> {formatCurrency(getTotalVolume(portfolioHistory.recent_trades))}</p>
                    </div>
                  ) : (
                    <div className="th-muted">No trade statistics available</div>
                  )}
                </div>
              </div>
            )}

            {portfolioHistory.source === 'no_database' && (
              <div className="th-empty">
                <p>MongoDB not connected - portfolio history unavailable</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default TradeHistory;