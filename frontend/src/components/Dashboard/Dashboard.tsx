import { useEffect, useRef, useState } from 'react';
import { tradingApi } from '../../api/tradingApi';
import './Dashboard.css';

function Dashboard() {
  const [status, setStatus] = useState<any>(null);
  const [sentiment, setSentiment] = useState<any>(null);
  const symbolInputRef = useRef<HTMLInputElement>(null);
  const sizeInputRef = useRef<HTMLInputElement>(null);

  const refreshStatus = () => {
    tradingApi.getStatus().then(setStatus).catch(() => {});
  };

  useEffect(() => {
    refreshStatus();
    tradingApi.getSentiment().then(setSentiment).catch(() => {});
  }, []);

  const startBot = () => {
    const symbol = symbolInputRef.current?.value ?? '';
    const positionSize = Number(sizeInputRef.current?.value ?? 0);
    tradingApi.startTrading({ symbol, position_size: positionSize }).then(refreshStatus);
  };

  const stopBot = () => {
    tradingApi.stopTrading().then(refreshStatus);
  };

  return (
    <>
      <h1>🤖AI Trading Bot Dashboard</h1>
      <div className="dashboard-grid">
        <div className="status-card">
          <h2>Trading Status</h2>
          <p>Status: {status?.status || 'Stopped'}</p>
          <p>Active Symbol: {status?.symbol || 'None'}</p>
        </div>

        <div className="sentiment-card">
          <h2>Market Sentiment</h2>
          <p>Current: {sentiment?.sentiment || 'Neutral'}</p>
          <p>Score: {sentiment?.score ?? 'N/A'}</p>
        </div>

        <div className="controls-card">
          <h2>Trading Controls</h2>
          <input ref={symbolInputRef} type="text" placeholder="Symbol (e.g., SPY)" defaultValue="SPY" />
          <input ref={sizeInputRef} type="number" placeholder="Position Size" defaultValue="0.5" step="0.1" />
          <button onClick={startBot}>Start Bot</button>
          <button onClick={stopBot}>Stop Bot</button>
        </div>
      </div>
    </>
  );
}

export default Dashboard;