# Bluestock Mutual Fund Analytics Platform

End-to-end mutual fund analytics capstone project covering data ingestion, cleaning, SQLite modelling, exploratory analysis, performance analytics, investor analytics, and a 4-page Power BI dashboard.

## Project Highlights

- Built a reusable Python ETL pipeline for 10 mutual fund datasets.
- Cleaned NAV, AUM, SIP, category inflow, folio, transaction, performance, portfolio holding, and benchmark data.
- Designed a SQLite star schema with fund, date, NAV, AUM, transaction, performance, SIP, benchmark, and holding tables.
- Created EDA notebooks with NAV trends, AUM growth, SIP trends, category inflow heatmap, investor demographics, folio growth, correlation, and sector allocation charts.
- Computed CAGR, Sharpe, Sortino, Alpha, Beta, VaR, CVaR, Max Drawdown, tracking error, HHI, and fund scorecard metrics.
- Built an interactive Power BI dashboard with 4 pages: Executive Overview, Fund Performance, Investor Analytics, and SIP & Market Trends.
- Prepared final PDF report and presentation deck.

## Folder Structure

```text
Bluestock_MF_Capstone_Submission/
├── README.md
├── requirements.txt
├── run_pipeline.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── db/
├── notebooks/
├── scripts/
├── sql/
├── docs/
├── dashboard/
└── reports/
    └── charts/
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

For Google Colab, upload the project folder, install `requirements.txt`, and run the notebooks from the project root.

## Run Pipeline

```bash
python run_pipeline.py
```

Useful scripts:

```bash
python scripts/data_ingestion.py
python scripts/etl_pipeline.py
python scripts/compute_metrics.py
python scripts/generate_charts.py
python scripts/recommender.py --risk Moderate --top-n 3
python scripts/live_nav_fetch.py
```

## Main Deliverables

- `dashboard/bluestock_mf_dashboard.pbix`
- `dashboard/Dashboard.pdf`
- `dashboard/Page1_Executive_Overview.png`
- `dashboard/Page2_Fund_Performance.png`
- `dashboard/Page3_Investor_Analytics.png`
- `dashboard/Page4_SIP_Market_Trends.png`
- `reports/Final_Report.pdf`
- `reports/Bluestock_MF_Presentation.pptx`
- `notebooks/03_eda_analysis.ipynb`
- `notebooks/04_performance_analytics.ipynb`
- `notebooks/05_advanced_analytics.ipynb`
- `reports/fund_scorecard.csv`
- `reports/alpha_beta.csv`
- `reports/var_cvar_report.csv`
- `sql/schema.sql`
- `sql/queries.sql`
- `docs/data_dictionary.md`
- `docs/data_quality_summary.md`

## Data Notes

- Benchmark data includes NIFTY50 and NIFTY100 in `10_benchmark_indices.csv`.
- Processed NAV data is sorted by fund and date, with missing dates handled for analytics.
- `mfapi.in` live NAV scripts require internet access.
- SQLite database is included for local review; if pushing to GitHub, avoid committing `.db` files unless explicitly required.
