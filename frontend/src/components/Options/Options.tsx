import { useEffect, useState } from 'react';
import { tradingApi } from '../../api/tradingApi';
import './Options.css';

const strategies = [
  { value: 'covered_call', label: 'Covered Call' },
  { value: 'protective_put', label: 'Protective Put' },
  { value: 'iron_condor', label: 'Iron Condor' },
];

function Options() {
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [selectedStrategy, setSelectedStrategy] = useState('covered_call');
  const [optionsChain, setOptionsChain] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadOptionsChain = (symbol: string) => {
    if (!symbol) return;
    setLoading(true);
    setError(null);
    tradingApi
      .getOptionsChain(symbol)
      .then(setOptionsChain)
      .catch(() => {
        setError(`Failed to load options for ${symbol}`);
        setOptionsChain({ calls: [], puts: [], underlying_price: 0 });
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadOptionsChain(selectedSymbol);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="options-container">
      <h1>🎯 Options Trading</h1>

      <div className="symbol-selector">
        <h2>Select Symbol</h2>
        <input
          value={selectedSymbol}
          onChange={(e) => setSelectedSymbol(e.target.value)}
          onBlur={() => loadOptionsChain(selectedSymbol)}
          type="text"
          placeholder="Enter symbol (e.g., ORCL)"
          className="symbol-input"
        />

        <select
          value={selectedStrategy}
          onChange={(e) => setSelectedStrategy(e.target.value)}
          className="strategy-select"
        >
          {strategies.map((strategy) => (
            <option key={strategy.value} value={strategy.value}>
              {strategy.label}
            </option>
          ))}
        </select>
      </div>

      {loading && <div className="loading">Loading options chain...</div>}

      {error && (
        <div className="error">
          {error}
          <button onClick={() => setError(null)}>x</button>
        </div>
      )}

      {optionsChain && (
        <>
          <div className="underlying-price">
            <h3>{selectedSymbol} Current Price: ${optionsChain.underlying_price}</h3>
          </div>

          <div className="options-tables">
            <div className="calls-selection">
              <h3>Call Options</h3>
              <table className="options-table">
                <thead>
                  <tr>
                    <th>Strike</th>
                    <th>Last Price</th>
                    <th>Bid</th>
                    <th>Ask</th>
                    <th>Volume</th>
                    <th>Expiry</th>
                  </tr>
                </thead>
                <tbody>
                  {(optionsChain.calls ?? []).map((call: any) => (
                    <tr key={call.strike}>
                      <td>${call?.strike}</td>
                      <td>${call?.last_price ?? 'N/A'}</td>
                      <td>${call?.bid ?? 'N/A'}</td>
                      <td>${call?.ask ?? 'N/A'}</td>
                      <td>${call?.volume ?? '0'}</td>
                      <td>${call?.expiry}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="puts-selection">
              <h3>Put Options</h3>
              <table className="options-table">
                <thead>
                  <tr>
                    <th>Strike</th>
                    <th>Last Price</th>
                    <th>Bid</th>
                    <th>Ask</th>
                    <th>Volume</th>
                    <th>Expiry</th>
                  </tr>
                </thead>
                <tbody>
                  {(optionsChain.puts ?? []).map((put: any) => (
                    <tr key={put.strike}>
                      <td>{put?.strike}</td>
                      <td>{put?.last_price ?? 'N/A'}</td>
                      <td>{put?.bid ?? 'N/A'}</td>
                      <td>{put?.ask ?? 'N/A'}</td>
                      <td>{put?.volume ?? '0'}</td>
                      <td>{put?.expiry}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default Options;