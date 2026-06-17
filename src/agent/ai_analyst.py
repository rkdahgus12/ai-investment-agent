"""
AI 분석 모듈
Ollama를 사용하여 기술적 분석 + 뉴스를 종합 판단
"""
import ollama
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import LOG_DIR
from src.analysis.technical import TechnicalAnalyzer
from src.data_collection.news_collector import NewsCollector


class AIAnalyst:
    """AI 종목 분석 클래스"""

    def __init__(self, model: str = "llama3.1:8b"):
        self.model = model
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    def _build_prompt(self, ticker: str, technical: dict, news: list) -> str:
        """AI 프롬프트 생성"""

        news_text = "\n".join([
            f"- [{item['source']}] {item['title']}"
            for item in news[:10]
        ])

        prompt = f"""
You are an expert stock analyst. Analyze the following data and provide a investment decision.

=== STOCK: {ticker} ===

[Technical Analysis]
- Current Price: 
- RSI: {technical.get('rsi')} (Under 30: oversold/buy signal, Over 70: overbought/sell signal)
- MACD: {technical.get('macd')} / Signal: {technical.get('macd_signal')}
- Bollinger Bands:  ~ 
- MA20:  / MA50:  / MA200: 
- Signals: {technical.get('signals')}

[Recent News]
{news_text}

=== INSTRUCTIONS ===
Based on the above data, provide your analysis in the following JSON format only.
Do not include any other text outside the JSON.

{{
    "ticker": "{ticker}",
    "decision": "BUY or SELL or HOLD",
    "score": 0,
    "confidence": 0.0,
    "reasons": [],
    "risk_level": "LOW or MEDIUM or HIGH",
    "target_price": 0.0,
    "stop_loss": 0.0
}}

Rules:
- score: 0-100 (higher means stronger buy signal)
- confidence: 0.0-1.0
- reasons: list of 3-5 specific reasons for your decision
- target_price: expected price target
- stop_loss: recommended stop loss price
"""
        return prompt

    def analyze(self, ticker: str) -> dict:
        """
        AI 종합 분석 수행

        Args:
            ticker: 종목 코드

        Returns:
            dict: AI 분석 결과
        """
        print(f"\n[AI 분석] {ticker} 분석 시작...")

        # 기술적 분석
        technical_analyzer = TechnicalAnalyzer()
        technical = technical_analyzer.analyze(ticker)

        if not technical:
            return {}

        # 뉴스 수집
        news_collector = NewsCollector()
        news = news_collector.get_news(ticker, days=3)

        # AI 프롬프트 생성
        prompt = self._build_prompt(ticker, technical, news)

        print(f"[AI 분석] Ollama {self.model} 분석 중...")

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response["message"]["content"].strip()

            # JSON 파싱
            if "`json" in content:
                content = content.split("`json")[1].split("`")[0].strip()
            elif "`" in content:
                content = content.split("`")[1].split("`")[0].strip()

            result = json.loads(content)
            result["analyzed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            result["technical"] = technical

            # 결과 출력
            print(f"\n{'='*50}")
            print(f"[AI 판단] {ticker}")
            print(f"  결정: {result.get('decision')}")
            print(f"  스코어: {result.get('score')}/100")
            print(f"  신뢰도: {result.get('confidence')}")
            print(f"  리스크: {result.get('risk_level')}")
            print(f"  목표가: ")
            print(f"  손절가: ")
            print(f"  이유:")
            for reason in result.get("reasons", []):
                print(f"    - {reason}")
            print(f"{'='*50}")

            # 로그 저장
            self._save_log(ticker, result)

            return result

        except json.JSONDecodeError as e:
            print(f"[오류] JSON 파싱 실패: {e}")
            print(f"[응답 원본] {content}")
            return {}
        except Exception as e:
            print(f"[오류] AI 분석 실패: {e}")
            return {}

    def _save_log(self, ticker: str, result: dict) -> None:
        """분석 결과 로그 저장"""
        log_file = LOG_DIR / f"ai_analysis_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
        print(f"[로그] {log_file}")


if __name__ == "__main__":
    analyst = AIAnalyst()
    tickers = ["AAPL", "TSLA", "NVDA"]
    for ticker in tickers:
        analyst.analyze(ticker)
