import { useEffect, useRef, useState } from 'react';
import { tradingApi } from '../../api/tradingApi';
import './Portfolio.css';

function Portfolio() {
  const [portfolio, setPortfolio] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const symbolInputRef = useRef<HTMLInputElement>(null);
  const qtyInputRef = useRef<HTMLInputElement>(null);

  const loadPortfolio = () => {
    tradingApi.getPortfolio().then(setPortfolio).catch(() => {});
  };

  useEffect(() => {
    loadPortfolio();
    const interval = setInterval(loadPortfolio, 30000);
    return () => clearInterval(interval);
  }, []);

  const placeTrade = (side: 'buy' | 'sell') => {
    const symbol = symbolInputRef.current?.value ?? '';
    const quantity = Number(qtyInputRef.current?.value ?? 0);
    tradingApi.placeTrade({ symbol, side, quantity }).then(loadPortfolio);
  };

  const refreshPortfolio = () => {
    setIsLoading(true);
    loadPortfolio();
    setTimeout(() => setIsLoading(false), 2000);
  };

  const isProfessional = portfolio?.source === 'professional';

  return (
    <>
      <h1>📊 Portfolio</h1>

      <div className={`mb-4 p-3 rounded-lg ${isProfessional ? 'bg-green-100 border border-green-300' : 'bg-yellow-100 border border-yellow-300'}`}>
        <div className="flex items-center gap-2">
          {isProfessional ? (
            <span className="text-green-600">✅ MongoDB Connected</span>
          ) : (
            <span className="text-yellow-600">⚠️ Demo Mode</span>
          )}
          <span className="text-sm text-gray-600">Data saved to database automatically</span>
        </div>
      </div>

      <div className="portfolio-grid">
        <div className="portfolio-summary">
          <h2>Account Summary</h2>
          <p>Cash: ${portfolio?.cash ?? '0.00'}</p>
          <p>Portfolio Value: ${portfolio?.portfolio_value ?? '0.00'}</p>
          <p>Positions: {portfolio?.positions?.length ?? '0.00'}</p>
          <p>Day P&amp;L: ${portfolio?.day_gain ?? '0.00'}</p>
        </div>

        <div className="positions">
          <h2>Positions ({portfolio?.positions?.length ?? 0})</h2>
          {(portfolio?.positions ?? []).map((position: any) => (
            <div key={position.symbol} className="position-item">
              <span>{position.symbol}: {position.qty} shares</span>
              <span>${position.market_value ?? '0.00'}</span>
            </div>
          ))}
        </div>

        <div className="trade-panel">
          <h2>Quick Trade</h2>
          <input ref={symbolInputRef} type="text" placeholder="Symbol" defaultValue="SPY" />
          <input ref={qtyInputRef} type="number" placeholder="Quantity" defaultValue="10" />
          <button onClick={() => placeTrade('buy')}>Buy</button>
          <button onClick={() => placeTrade('sell')}>Sell</button>
          <button onClick={refreshPortfolio} disabled={isLoading}>
            🔄 {isLoading ? 'Loading...' : 'Refresh Portfolio'}
          </button>
        </div>
      </div>
    </>
  );
}

export default Portfolio;