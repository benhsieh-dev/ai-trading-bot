# Mock implementation for development without ML dependencies
from typing import Tuple 
import random

labels = ["positive", "negative", "neutral"]

def estimate_sentiment(news):
    """
    Mock sentiment analysis function for development.
    Replace with actual FinBERT implementation when ML dependencies are available.
    """
    if news and len(news) > 0:
        # Simple mock logic based on keywords
        text = " ".join(news).lower()
        
        if any(word in text for word in ["good", "great", "profit", "gain", "up", "rise", "bull"]):
            return 0.85, "positive"
        elif any(word in text for word in ["bad", "loss", "down", "fall", "bear", "crash"]):
            return 0.75, "negative"
        else:
            # Random sentiment for neutral cases
            sentiment = random.choice(labels)
            probability = random.uniform(0.6, 0.9)
            return probability, sentiment
    else:
        return 0, labels[-1]


if __name__ == "__main__":
    tensor, sentiment = estimate_sentiment(['markets responded negatively to the news!','traders were displeased!'])
    print(tensor, sentiment)
    print(torch.cuda.is_available())