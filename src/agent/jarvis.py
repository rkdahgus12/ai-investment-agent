"""
자비스 메인 에이전트
모든 모듈을 통합하여 자율적으로 시장 분석 및 매매 신호 생성
"""
import json
import time
import schedule
from datetime import datetime
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import LOG_DIR
from src.agent.ai_analyst import AIAnalyst


# 관심 종목 리스트
WATCHLIST = ["AAPL", "TSLA", "NVDA", "MSFT", "AMZN"]

# 리스크 관리 설정
RISK_CONFIG = {
    "max_position_pct": 0.10,    # 단일 종목 최대 10%
    "stop_loss_pct": -0.05,       # 손절 -5%
    "take_profit_pct": 0.15,      # 익절 +15%
    "daily_loss_limit_pct": 0.03, # 일일 손실 한도 3%
    "max_drawdown_pct": 0.15,     # 최대 낙폭 15%
    "min_score": 70,              # 최소 매수 스코어
    "min_confidence": 0.7,        # 최소 신뢰도
}


class JarvisAgent:
    """자비스 자율 투자 에이전트"""

    def __init__(self):
        self.analyst = AIAnalyst()
        self.portfolio = {}
        self.daily_pnl = 0.0
        self.is_running = False
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"""
╔══════════════════════════════════════╗
║     JARVIS 투자 에이전트 시작        ║
║     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}         ║
╚══════════════════════════════════════╝
        """)

    def analyze_market(self) -> list:
        """전체 관심 종목 분석"""
        print(f"\n[자비스] 시장 분석 시작 - {datetime.now().strftime('%H:%M:%S')}")
        print(f"[자비스] 분석 종목: {WATCHLIST}")

        results = []
        for ticker in WATCHLIST:
            result = self.analyst.analyze(ticker)
            if result:
                results.append(result)
            time.sleep(1)

        return results

    def check_risk(self, result: dict) -> bool:
        """
        리스크 관리 체크

        Returns:
            bool: 매수 가능 여부
        """
        # 일일 손실 한도 체크
        if self.daily_pnl <= -RISK_CONFIG["daily_loss_limit_pct"]:
            print(f"[리스크] 일일 손실 한도 초과 - 거래 중단")
            return False

        # 스코어 체크
        if result.get("score", 0) < RISK_CONFIG["min_score"]:
            return False

        # 신뢰도 체크
        if result.get("confidence", 0) < RISK_CONFIG["min_confidence"]:
            return False

        return True

    def generate_signals(self, results: list) -> list:
        """매매 신호 생성"""
        signals = []

        for result in results:
            ticker = result.get("ticker")
            decision = result.get("decision")
            score = result.get("score", 0)
            confidence = result.get("confidence", 0)

            if decision == "BUY" and self.check_risk(result):
                signal = {
                    "ticker": ticker,
                    "action": "BUY",
                    "score": score,
                    "confidence": confidence,
                    "reasons": result.get("reasons", []),
                    "risk_level": result.get("risk_level"),
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                signals.append(signal)
                print(f"\n[신호] 매수 신호 발생!")
                print(f"  종목: {ticker}")
                print(f"  스코어: {score}/100")
                print(f"  신뢰도: {confidence}")
                print(f"  이유: {result.get('reasons', [])}")

            elif decision == "SELL" and ticker in self.portfolio:
                signal = {
                    "ticker": ticker,
                    "action": "SELL",
                    "score": score,
                    "confidence": confidence,
                    "reasons": result.get("reasons", []),
                    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                signals.append(signal)
                print(f"\n[신호] 매도 신호 발생!")
                print(f"  종목: {ticker}")

        return signals

    def save_signals(self, signals: list) -> None:
        """신호 로그 저장"""
        if not signals:
            return
        log_file = LOG_DIR / f"signals_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            for signal in signals:
                f.write(json.dumps(signal, ensure_ascii=False) + "\n")
        print(f"\n[로그] {len(signals)}개 신호 저장 완료")

    def run_cycle(self) -> None:
        """1회 분석 사이클 실행"""
        print(f"\n{'='*50}")
        print(f"[자비스] 분석 사이클 시작")
        print(f"{'='*50}")

        # 시장 분석
        results = self.analyze_market()

        # 매매 신호 생성
        signals = self.generate_signals(results)

        # 신호 저장
        self.save_signals(signals)

        print(f"\n[자비스] 사이클 완료")
        print(f"  분석 종목: {len(results)}개")
        print(f"  매매 신호: {len(signals)}개")
        print(f"{'='*50}\n")

    def run_scheduled(self) -> None:
        """스케줄러 실행 (장 시작 전 자동 분석)"""
        print("[자비스] 스케줄러 모드 시작")
        print("  - 매일 09:00 시장 분석 실행")
        print("  - 매일 13:00 시장 분석 실행")
        print("  - 중단하려면 Ctrl+C")

        schedule.every().day.at("09:00").do(self.run_cycle)
        schedule.every().day.at("13:00").do(self.run_cycle)

        while True:
            schedule.run_pending()
            time.sleep(60)

    def run_now(self) -> None:
        """즉시 1회 실행"""
        self.run_cycle()


if __name__ == "__main__":
    jarvis = JarvisAgent()
    
    # 즉시 1회 실행
    jarvis.run_now()
