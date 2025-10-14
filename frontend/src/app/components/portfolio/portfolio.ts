import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import {isPlatformBrowser, NgForOf} from '@angular/common';
import { TradingService } from '../../services/trading';
import { Observable } from 'rxjs';
import { AsyncPipe, CommonModule } from '@angular/common';

@Component({
  selector: 'app-portfolio',
  imports: [AsyncPipe, CommonModule],
  templateUrl: './portfolio.html',
  styleUrl: './portfolio.css'
})

export class PortfolioComponent implements OnInit {
  portfolio$!: Observable<any>;
  orders$!: Observable<any>;

  constructor(
    private tradingService: TradingService,
    @Inject(PLATFORM_ID) private platformId: Object) {}

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.portfolio$ = this.tradingService.getPortfolio();
      this.orders$ = this.tradingService.getOrders();
    }
  }
  placeTrade(symbol: string, side: string, quantity: number) {
    if (isPlatformBrowser(this.platformId)) {
      this.tradingService.placeTrade({symbol, side, quantity})
        .subscribe(result => {
          this.portfolio$ = this.tradingService.getPortfolio();
        });
    }
  }
}
