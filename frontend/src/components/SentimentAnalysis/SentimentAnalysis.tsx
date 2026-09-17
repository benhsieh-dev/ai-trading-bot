import { useState } from 'react';
import { tradingApi } from '../../api/tradingApi';
import './SentimentAnalysis.css';

interface SentimentResults {
  sentiment: string;
  score: number;
  confidence: number;
  articleCount: number;
  timestamp: string;
}

function getSentimentColor(sentiment: string): string {
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

function titlecase(value: string): string {
  if (!value) return value;
  return value.charAt(0).toUpperCase() + value.slice(1).toLowerCase();
}

function SentimentAnalysis() {
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [selectedPeriod, setSelectedPeriod] = useState(3);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [sentimentResults, setSentimentResults] = useState<SentimentResults | null>(null);
  const [newsArticles, setNewsArticles] = useState<any[]>([]);
  const [isLoadingNews, setIsLoadingNews] = useState(false);

  const loadNews = (symbol: string) => {
    setIsLoadingNews(true);
    tradingApi
      .getNews(symbol)
      .then((news: any) => {
        setNewsArticles(news.articles || news || []);
      })
      .catch((error) => {
        console.error('Error fetching news:', error);
      })
      .finally(() => setIsLoadingNews(false));
  };

  const analyzeSentiment = () => {
    if (!selectedSymbol.trim()) return;

    setIsAnalyzing(true);
    setSentimentResults(null);

    const symbol = selectedSymbol.toUpperCase();
    tradingApi
      .getSentiment(symbol)
      .then((data: any) => {
        setSentimentResults({
          sentiment: data.sentiment,
          score: data.score || 0,
          confidence: data.confidence || 0,
          articleCount: data.article_count || 0,
          timestamp: new Date().toISOString(),
        });
        setIsAnalyzing(false);
        loadNews(symbol);
      })
      .catch((error) => {
        console.error('Error fetching sentiment analysis:', error);
        console.error('Error status:', error.status);
        console.error('Error URL:', error.url);
        console.error('Error message:', error.message);
        setIsAnalyzing(false);
      });
  };

  return (
    <>
      <div className="analysis-form">
        <div className="form-group">
          <label>Symbol to Analyze:</label>
          <input
            type="text"
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            placeholder="e.g., SPY, AAPL, NVDA"
            style={{ textTransform: 'uppercase' }}
          />
        </div>

        <div className="form-group">
          <label>News Lookback Period</label>
          <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(Number(e.target.value))}>
            <option value={1}>1 Day</option>
            <option value={3}>3 Days</option>
            <option value={7}>7 Days</option>
            <option value={14}>14 Days</option>
          </select>
        </div>

        <button onClick={analyzeSentiment} disabled={isAnalyzing} className="analyze-btn">
          {isAnalyzing ? '🔄 Analyzing...' : '🧠 Analyze Sentiment'}
        </button>
      </div>

      {sentimentResults && (
        <>
          <div className="sentiment-results">
            <h5>Sentiment Analysis Results</h5>
            <div className="results-grid">
              <div className="result-card">
                <div className="metric-value" style={{ color: getSentimentColor(sentimentResults.sentiment) }}>
                  {titlecase(sentimentResults.sentiment)}
                </div>
                <div className="metric-label">Sentiment</div>
              </div>

              <div className="result-card">
                <div className="metric-value">{(sentimentResults.confidence * 100).toFixed(1)}%</div>
                <div className="metric-label">AI Confidence</div>
              </div>

              <div className="result-card">
                <div className="metric-value">{sentimentResults.articleCount}</div>
                <div className="metric-label">News Articles</div>
              </div>
            </div>

            <div className="analysis-timestamp">
              Last Updated: {new Date(sentimentResults.timestamp).toLocaleString()}
            </div>
          </div>

          <div className="news-section">
            <h5>📰 Related News</h5>

            {isLoadingNews ? (
              <div>Loading news...</div>
            ) : newsArticles.length === 0 ? (
              <div>No recent news articles found.</div>
            ) : (
              <div className="news-list">
                {newsArticles.map((article) => (
                  <div key={article.url} className="news-item">
                    <a href={article.url} target="_blank" rel="noreferrer">
                      {article.headline || article.title}
                    </a>
                    <div className="news-meta">
                      <span>{article.source || 'Unknown Source'}</span>
                      <span>{new Date(article.created_at || article.publishedAt).toLocaleString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </>
  );
}

export default SentimentAnalysis;