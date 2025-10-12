import { Component, OnInit } from '@angular/core';
import {TradingService} from '../../services/trading';
import {Observable} from 'rxjs';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-portfolio',
  imports: [AsyncPipe],
  templateUrl: './portfolio.html',
  styleUrl: './portfolio.css'
})

export class PortfolioComponent implements OnInit {
  portfolio$!: Observable<any>;
  orders$!: Observable<any>;

  constructor(private tradingService: TradingService) {}

  ngOnInit() {
    this.portfolio$ = this.tradingService.getPortfolio();
    this.orders$ = this.tradingService.getOrders();
  }
  placeTrade(symbol: string, side: string, quantity: number) {
    this.tradingService.placeTrade({symbol, side, quantity})
      .subscribe(result => {
      this.portfolio$ = this.tradingService.getPortfolio();
    })
  }
}
