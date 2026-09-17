// API base is relative in both dev (proxied by Vite, see vite.config.ts)
// and production (served by the same Flask app), matching the Angular
// environment.apiUrl behavior this replaces.
const API_BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const error: any = new Error(`Request to ${path} failed with status ${res.status}`);
    error.status = res.status;
    error.url = res.url;
    throw error;
  }
  return res.json();
}

export const tradingApi = {
  getStatus: () => request<any>('/status'),
  startTrading: (data: { symbol: string; position_size: number }) =>
    request<any>('/start', { method: 'POST', body: JSON.stringify(data) }),
  stopTrading: () => request<any>('/stop', { method: 'POST', body: JSON.stringify({}) }),
  getPortfolio: () => request<any>('/portfolio'),
  getSentiment: (symbol?: string) =>
    request<any>(symbol ? `/sentiment/${symbol}` : '/sentiment'),
  runBacktest: (data: any) =>
    request<any>('/backtest', { method: 'POST', body: JSON.stringify(data) }),
  placeTrade: (data: { symbol: string; side: string; quantity: number }) =>
    request<any>('/trade', { method: 'POST', body: JSON.stringify(data) }),
  getOrders: () => request<any>('/orders'),
  getOptionsChain: (symbol: string) => request<any>(`/options/${symbol}`),
  getNews: (symbol: string) => request<any>(`/news/${symbol}`),
  refreshSentiment: () => request<any>('/refresh_sentiment'),

  // Trade/portfolio history (PostgreSQL-backed)
  getTradeHistory: (userId = 'default', limit = 100) =>
    request<any>(`/trade-history?user_id=${userId}&limit=${limit}`),
  getPortfolioHistory: (userId = 'default') =>
    request<any>(`/portfolio-history?user_id=${userId}`),
};