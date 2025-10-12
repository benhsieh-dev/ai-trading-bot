import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class TradingService {
  private apiUrl = '/api';

  constructor(private http: HttpClient) {}

    getStatus() { return this.http.get(`${this.apiUrl}/status`);}
    startTrading(data: any) { return this.http.post(`${this.apiUrl}/start`, data);}
    stopTrading() { return this.http.post(`${this.apiUrl}/stop`, {});}
    getPortfolio() { return this.http.get(`${this.apiUrl}/portfolio`);}
    getSentiment(symbol?: string) {
      const url = symbol ? `${this.apiUrl}/sentiment/${symbol}` : `${this.apiUrl}/sentiment`;
      return this.http.get(url);
    }
    runBacktest(data: any) { return this.http.post(`${this.apiUrl}/backtest`, data);}
    placeTrade(data: any) { return this.http.post(`${this.apiUrl}/trade`, data);}
    getOrders() { return this.http.get(`${this.apiUrl}/orders`);}
}
