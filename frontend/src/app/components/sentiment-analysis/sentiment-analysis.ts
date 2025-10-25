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

  newsArticles: any[] = [];
  isLoadingNews: boolean = false;

  analyzeSentiment() {
    if (!this.selectedSymbol.trim()) return;

    this.isAnalyzing = true;
    this.sentimentResults = null;

    console.log('Calling getSentiment for:', this.selectedSymbol.toUpperCase());
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
          // Automatically load news after sentiment analysis
          this.loadNews();
        },
        error: (error) => {
          console.error('Error fetching sentiment analysis:', error);
          console.error('Error status:', error.status);
          console.error('Error URL:', error.url);
          console.error('Error message:', error.message);
          this.isAnalyzing = false;
        }
      });
  }

  loadNews() {
    this.isLoadingNews = true;
    this.tradingService.getNews(this.selectedSymbol.toUpperCase())
      .subscribe({
        next: (news: any) => {
          this.newsArticles = news.articles || news || [];
          this.isLoadingNews = false;
        },
        error: (error) => {
          console.error('Error fetching news:', error);
          this.isLoadingNews = false;
        }
      })
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
