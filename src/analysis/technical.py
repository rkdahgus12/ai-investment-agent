"""
기술적 분석 모듈
RSI, MACD, 볼린저밴드, 이동평균선 계산
"""
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.data_collection.market_data import MarketDataCollector


class TechnicalAnalyzer:
    """기술적 분석 클래스"""

    def analyze(self, ticker: str) -> dict:
        """
        종목 기술적 분석 수행

        Args:
            ticker: 종목 코드

        Returns:
            dict: 분석 결과
        """
        collector = MarketDataCollector()
        df = collector.get_stock_data(ticker, period="1y")

        if df.empty:
            return {}

        close = df["Close"]

        # RSI
        rsi = RSIIndicator(close=close, window=14)
        rsi_value = round(float(rsi.rsi().iloc[-1]), 2)

        # MACD
        macd = MACD(close=close)
        macd_value = round(float(macd.macd().iloc[-1]), 2)
        macd_signal = round(float(macd.macd_signal().iloc[-1]), 2)
        macd_diff = round(float(macd.macd_diff().iloc[-1]), 2)

        # 볼린저밴드
        bb = BollingerBands(close=close, window=20)
        bb_upper = round(float(bb.bollinger_hband().iloc[-1]), 2)
        bb_lower = round(float(bb.bollinger_lband().iloc[-1]), 2)
        bb_mid = round(float(bb.bollinger_mavg().iloc[-1]), 2)
        current_price = round(float(close.iloc[-1]), 2)

        # 이동평균선
        ma20 = round(float(close.rolling(20).mean().iloc[-1]), 2)
        ma50 = round(float(close.rolling(50).mean().iloc[-1]), 2)
        ma200 = round(float(close.rolling(200).mean().iloc[-1]), 2)

        # 신호 판단
        signals = []
        if rsi_value < 30:
            signals.append("RSI 과매도 구간 (매수 신호)")
        elif rsi_value > 70:
            signals.append("RSI 과매수 구간 (매도 신호)")

        if macd_diff > 0 and macd_value > macd_signal:
            signals.append("MACD 골든크로스 (매수 신호)")
        elif macd_diff < 0 and macd_value < macd_signal:
            signals.append("MACD 데드크로스 (매도 신호)")

        if current_price < bb_lower:
            signals.append("볼린저밴드 하단 이탈 (매수 신호)")
        elif current_price > bb_upper:
            signals.append("볼린저밴드 상단 이탈 (매도 신호)")

        if ma20 > ma50:
            signals.append("단기 이평선 상향 (상승 추세)")
        else:
            signals.append("단기 이평선 하향 (하락 추세)")

        result = {
            "ticker": ticker,
            "current_price": current_price,
            "rsi": rsi_value,
            "macd": macd_value,
            "macd_signal": macd_signal,
            "macd_diff": macd_diff,
            "bb_upper": bb_upper,
            "bb_mid": bb_mid,
            "bb_lower": bb_lower,
            "ma20": ma20,
            "ma50": ma50,
            "ma200": ma200,
            "signals": signals
        }

        print(f"\n[기술적 분석] {ticker}")
        print(f"  현재가: {current_price}")
        print(f"  RSI: {rsi_value}")
        print(f"  MACD: {macd_value} / Signal: {macd_signal}")
        print(f"  볼린저밴드: {bb_lower} ~ {bb_upper}")
        print(f"  MA20: {ma20} / MA50: {ma50} / MA200: {ma200}")
        print(f"  신호: {signals}")

        return result


if __name__ == "__main__":
    analyzer = TechnicalAnalyzer()
    tickers = ["AAPL", "TSLA", "NVDA"]
    for ticker in tickers:
        analyzer.analyze(ticker)
