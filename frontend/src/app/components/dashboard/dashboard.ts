import { Component, OnInit } from '@angular/core';
import {TradingService} from '../../services/trading';
import {Observable} from 'rxjs';
import { AsyncPipe } from '@angular/common';

@Component({
  selector: 'app-dashboard',
  imports: [AsyncPipe],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class DashboardComponent implements OnInit{
  tradingStatus$!: Observable<any>;
  sentiment$!: Observable<any>;

  constructor(private tradingService: TradingService) {}

  ngOnInit() {
    this.tradingStatus$ = this.tradingService.getStatus();
    this.sentiment$ = this.tradingService.getSentiment();
  }

  startBot(symbol: string, positionSize: number) {
    this.tradingService.startTrading({symbol, position_size: positionSize})
    .subscribe(result => {
      this.tradingStatus$ = this.tradingService.getStatus();
    });
  }
}
