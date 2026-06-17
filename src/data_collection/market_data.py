"""
시장 데이터 수집 모듈
yfinance를 사용하여 미국 주식 데이터 수집
"""
import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import MARKET_DIR

class MarketDataCollector:
    """주가 데이터 수집 클래스"""

    def __init__(self):
        MARKET_DIR.mkdir(parents=True, exist_ok=True)

    def get_stock_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """
        주가 데이터 수집
        
        Args:
            ticker: 종목 코드 (예: AAPL, TSLA)
            period: 기간 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)
        
        Returns:
            DataFrame: OHLCV 데이터
        """
        print(f"[데이터 수집] {ticker} 데이터 수집 중...")
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            print(f"[경고] {ticker} 데이터 없음")
            return pd.DataFrame()
        
        df.index = pd.to_datetime(df.index)
        print(f"[완료] {ticker} {len(df)}일 데이터 수집 완료")
        return df

    def save_stock_data(self, ticker: str, period: str = "1y") -> Path:
        """데이터 수집 후 CSV 저장"""
        df = self.get_stock_data(ticker, period)
        
        if df.empty:
            return None
        
        file_path = MARKET_DIR / f"{ticker}_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(file_path)
        print(f"[저장] {file_path}")
        return file_path

    def get_multiple_stocks(self, tickers: list, period: str = "1y") -> dict:
        """여러 종목 동시 수집"""
        result = {}
        for ticker in tickers:
            df = self.get_stock_data(ticker, period)
            if not df.empty:
                result[ticker] = df
        return result


if __name__ == "__main__":
    collector = MarketDataCollector()
    
    # 테스트
    tickers = ["AAPL", "TSLA", "NVDA"]
    for ticker in tickers:
        collector.save_stock_data(ticker)
