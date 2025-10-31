import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { TradingService } from '../../services/trading';
import { Observable } from 'rxjs';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-trade-history',
  imports: [AsyncPipe, CommonModule],
  templateUrl: './trade-history.html',
  styleUrls: ['./trade-history.css']
})
export class TradeHistoryComponent implements OnInit {
  tradeHistory$!: Observable<any>;
  portfolioHistory$!: Observable<any>;
  isLoading = false;

  constructor(
    private tradingService: TradingService,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.loadTradeHistory();
      this.loadPortfolioHistory();
      
      // Refresh every 30 seconds
      setInterval(() => {
        this.loadTradeHistory();
        this.loadPortfolioHistory();
      }, 30000);
    }
  }

  loadTradeHistory() {
    this.tradeHistory$ = this.tradingService.getTradeHistory();
  }

  loadPortfolioHistory() {
    this.portfolioHistory$ = this.tradingService.getPortfolioHistory();
  }

  refreshData() {
    this.isLoading = true;
    this.loadTradeHistory();
    this.loadPortfolioHistory();
    setTimeout(() => this.isLoading = false, 1000);
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleString();
  }

  getTradeColor(side: string): string {
    return side === 'buy' ? 'text-green-600' : 'text-red-600';
  }

  getBuyOrdersCount(trades: any[]): number {
    return trades.filter(trade => trade.side === 'buy').length;
  }

  getSellOrdersCount(trades: any[]): number {
    return trades.filter(trade => trade.side === 'sell').length;
  }

  getTotalVolume(trades: any[]): number {
    return trades.reduce((total, trade) => total + (trade.total_value || 0), 0);
  }
}