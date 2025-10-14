import { Component, OnInit, Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
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

  constructor(
    private tradingService: TradingService,
    @Inject(PLATFORM_ID) private platformId: Object) {}

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.tradingStatus$ = this.tradingService.getStatus();
      this.sentiment$ = this.tradingService.getSentiment();
    }
  }

  startBot(symbol: string, positionSize: number) {
    if (isPlatformBrowser(this.platformId)) {
      this.tradingService.startTrading({symbol, position_size: positionSize})
        .subscribe(result => {
          this.tradingStatus$ = this.tradingService.getStatus();
        });
    }
  }

  stopBot() {
    if (isPlatformBrowser(this.platformId)) {
      this.tradingService.stopTrading()
        .subscribe(result => {
          this.tradingStatus$ = this.tradingService.getStatus();
        });
    }
  }
}
