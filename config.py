"""Shared project paths and constants for the Bluestock MF capstone."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DB_DIR = DATA_DIR / "db"
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"
CHARTS_DIR = REPORTS_DIR / "charts"
DOCS_DIR = PROJECT_ROOT / "docs"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"
CONTEXT_DIR = PROJECT_ROOT / "context"

DB_PATH = DB_DIR / "bluestock_mf.db"

RAW_FILES = {
    "fund_master": "01_fund_master.csv",
    "nav_history": "02_nav_history.csv",
    "aum_by_fund_house": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "scheme_performance": "07_scheme_performance.csv",
    "investor_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv",
}

KEY_SCHEME_CODES = {
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip",
}

LIVE_NAV_SCHEMES = {
    125497: "HDFC Top 100 Direct",
    119551: "SBI Bluechip",
    120503: "ICICI Bluechip",
    118632: "Nippon Large Cap",
    119092: "Axis Bluechip",
    120841: "Kotak Bluechip",
}

BENCHMARK_INDICES = ["NIFTY50", "NIFTY100", "NIFTY500", "NIFTY_MIDCAP150", "BSE_SMALLCAP"]
RISK_FREE_RATE_ANNUAL = 0.065


def ensure_project_dirs() -> None:
    """Create the standard project folders if they do not already exist."""
    for path in [
        RAW_DIR,
        PROCESSED_DIR,
        DB_DIR,
        NOTEBOOK_DIR,
        SQL_DIR,
        REPORTS_DIR,
        CHARTS_DIR,
        DOCS_DIR,
        DASHBOARD_DIR,
        CONTEXT_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)

