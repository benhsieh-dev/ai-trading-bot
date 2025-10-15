import {Component, Inject, OnInit} from '@angular/core';
import {CommonModule, isPlatformBrowser, AsyncPipe} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {TradingService} from '../../services/trading';
import {Observable, BehaviorSubject, catchError, of } from 'rxjs';
import {PLATFORM_ID} from '@angular/core';

@Component({
  selector: 'app-options',
  imports: [AsyncPipe, CommonModule, FormsModule],
  templateUrl: './options.html',
  styleUrl: './options.css',
})

export class OptionsComponent implements OnInit {
  optionsChain$!: Observable<any>;
  private loadingSubject = new BehaviorSubject<boolean>(false);
  private errorSubject = new BehaviorSubject<string | null>(null);
  loading$ = this.loadingSubject.asObservable();
  error$ = this.errorSubject.asObservable();

    constructor(
      private tradingService: TradingService,
      @Inject(PLATFORM_ID) private platformId: Object
    ) { }



    selectedSymbol = 'SPY';
    selectedStrategy = 'covered_call';

    strategies = [
      { value: 'covered_call', label: 'Covered Call' },
      { value: 'protective_put', label: 'Protective Put' },
      { value: 'iron_condor', label: 'Iron Condor' }
    ]

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)){
      this.loadOptionsChain();
    }
  }

  loadOptionsChain() {
      if (!this.selectedSymbol) return;

      this.loadingSubject.next(true);
      this.errorSubject.next(null);

      this.optionsChain$ = this.tradingService.getOptionsChain(this.selectedSymbol).pipe(
        catchError(error => {
          this.errorSubject.next(`Failed to load options for ${this.selectedSymbol}`);
          return of({ calls: [], puts: [], underlying_price: 0 });
        })
      );
      this.loadingSubject.next(false);
  }

  onSymbolChange() {
      this.loadOptionsChain();
  }
  clearError() {
      this.errorSubject.next(null);
  }
}
