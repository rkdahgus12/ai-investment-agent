from pathlib import Path

# 외장 SSD 경로
SSD_ROOT = Path("D:/ai-investment-agent")

DATA_DIR        = SSD_ROOT / "data"
MARKET_DIR      = DATA_DIR / "market"
NEWS_DIR        = DATA_DIR / "news"
FINANCIAL_DIR   = DATA_DIR / "financial"
DB_DIR          = SSD_ROOT / "db"
LOG_DIR         = SSD_ROOT / "logs"
BACKTEST_DIR    = SSD_ROOT / "backtest_results"
ENV_FILE        = SSD_ROOT / ".env"
