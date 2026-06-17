"""
뉴스 수집 모듈
Finnhub API를 사용하여 미국 주식 뉴스 수집
"""
import finnhub
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import os
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import NEWS_DIR, ENV_FILE

load_dotenv(ENV_FILE)


class NewsCollector:
    """뉴스 수집 클래스"""

    def __init__(self):
        NEWS_DIR.mkdir(parents=True, exist_ok=True)
        api_key = os.getenv("FINNHUB_API_KEY")
        self.client = finnhub.Client(api_key=api_key)

    def get_news(self, ticker: str, days: int = 7) -> list:
        """
        종목 관련 뉴스 수집

        Args:
            ticker: 종목 코드 (예: AAPL)
            days: 최근 몇 일치 뉴스

        Returns:
            list: 뉴스 기사 목록
        """
        print(f"\n[뉴스 수집] {ticker} 관련 뉴스 수집 중...")

        date_to = datetime.now().strftime("%Y-%m-%d")
        date_from = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        try:
            news = self.client.company_news(ticker, _from=date_from, to=date_to)
        except Exception as e:
            print(f"  [오류] {e}")
            return []

        articles = []
        for item in news:
            articles.append({
                "ticker": ticker,
                "source": item.get("source", ""),
                "title": item.get("headline", ""),
                "summary": item.get("summary", "")[:500],
                "link": item.get("url", ""),
                "published": datetime.fromtimestamp(item.get("datetime", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                "collected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        print(f"  [완료] {len(articles)}개 뉴스 수집")
        for i, article in enumerate(articles[:3], 1):
            print(f"  [{i}] {article['source']}: {article['title'][:60]}...")

        return articles

    def save_news(self, ticker: str) -> Path:
        """뉴스 수집 후 CSV 저장"""
        articles = self.get_news(ticker)

        if not articles:
            print(f"  [경고] {ticker} 뉴스 없음")
            return None

        df = pd.DataFrame(articles)
        file_path = NEWS_DIR / f"{ticker}_news_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"  [저장] {file_path}")
        return file_path


if __name__ == "__main__":
    collector = NewsCollector()
    tickers = ["AAPL", "TSLA", "NVDA"]
    for ticker in tickers:
        collector.save_news(ticker)
