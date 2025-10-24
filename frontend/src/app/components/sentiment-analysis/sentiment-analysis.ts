import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { TradingService } from '../../services/trading';

@Component({
  selector: 'app-sentiment-analysis',
  imports: [FormsModule, CommonModule],
  templateUrl: './sentiment-analysis.html',
  styleUrl: './sentiment-analysis.css'
})
export class SentimentAnalysisComponent {
  
  constructor(private tradingService: TradingService) {}
  selectedSymbol = 'SPY';
  selectedPeriod: number = 3;
  isAnalyzing: boolean = false;

  sentimentResults: {
    sentiment: string;
    score: number;
    confidence: number;
    articleCount: number;
    timestamp: string;
  } | null = null;

  analyzeSentiment() {
    if (!this.selectedSymbol.trim()) return;

    this.isAnalyzing = true;
    this.sentimentResults = null;

    this.tradingService.getSentiment(this.selectedSymbol.toUpperCase())
      .subscribe({
        next: (data: any) => {
          this.sentimentResults = {
            sentiment: data.sentiment,
            score: data.score || 0,
            confidence: data.confidence || 0,
            articleCount: data.article_count || 0,
            timestamp: new Date().toISOString()
          };
          this.isAnalyzing = false;
        },
        error: (error) => {
          console.error('Error fetching sentiment analysis:', error);
          this.isAnalyzing = false;
        }
      });
  }

  getSentimentColor(sentiment: string): string {
    switch (sentiment?.toLowerCase()) {
      case 'bullish':
      case 'positive':
        return '#27ae60';
      case 'bearish':
      case 'negative':
        return '#e74c3c';
      default:
        return '#7f8c8d';
    }
  }
}
