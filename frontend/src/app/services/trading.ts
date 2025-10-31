import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class TradingService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

    getStatus() { return this.http.get(`${this.apiUrl}/status`);}
    startTrading(data: any) { return this.http.post(`${this.apiUrl}/start`, data);}
    stopTrading() { return this.http.post(`${this.apiUrl}/stop`, {});}
    getPortfolio() { return this.http.get(`${this.apiUrl}/portfolio`);}
    getSentiment(symbol?: string) {
      const url = symbol ? `${this.apiUrl}/sentiment/${symbol}` : `${this.apiUrl}/sentiment`;
      console.log('TradingService calling URL:', url);
      return this.http.get(url);
    }
    runBacktest(data: any) { return this.http.post(`${this.apiUrl}/backtest`, data);}
    placeTrade(data: any) { return this.http.post(`${this.apiUrl}/trade`, data);}
    getOrders() { return this.http.get(`${this.apiUrl}/orders`);}
    getOptionsChain(symbol: string) { return this.http.get(`${this.apiUrl}/options/${symbol}`);}
    getNews(symbol: string) { return this.http.get(`${this.apiUrl}/news/${symbol}`);}
    refreshSentiment() { return this.http.get(`${this.apiUrl}/refresh_sentiment`);}
    
    // MongoDB integration methods
    getTradeHistory(userId = 'default', limit = 100) {
      return this.http.get(`${this.apiUrl}/trade-history?user_id=${userId}&limit=${limit}`);
    }
    
    getPortfolioHistory(userId = 'default') {
      return this.http.get(`${this.apiUrl}/portfolio-history?user_id=${userId}`);
    }
}
