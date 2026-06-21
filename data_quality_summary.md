# Data Quality Summary

## Key Checks

- All `40` AMFI codes in fund master exist in NAV history.
- NAV source rows: `46,000`; calendar-filled processed rows: `64,320`.
- Forward-filled weekend/holiday NAV rows: `18,320`.
- NAV values are positive after cleaning: `True`.
- Transaction amounts are positive after cleaning: `True`.
- Performance anomaly rows flagged: `0`.

## SQLite Row Audit

| Dataset | Table | Processed Rows | SQLite Rows | Matches |
| --- | --- | ---: | ---: | --- |
| `fund_master` | `dim_fund` | 40 | 40 | True |
| `dim_date` | `dim_date` | 1,608 | 1,608 | True |
| `dim_investor` | `dim_investor` | 5,000 | 5,000 | True |
| `nav_history` | `fact_nav` | 64,320 | 64,320 | True |
| `investor_transactions` | `fact_transactions` | 32,778 | 32,778 | True |
| `scheme_performance` | `fact_performance` | 40 | 40 | True |
| `aum_by_fund_house` | `fact_aum` | 90 | 90 | True |
| `monthly_sip_inflows` | `fact_sip` | 48 | 48 | True |
| `category_inflows` | `fact_category_inflows` | 144 | 144 | True |
| `industry_folio_count` | `fact_folio_count` | 21 | 21 | True |
| `portfolio_holdings` | `fact_portfolio_holdings` | 322 | 322 | True |
| `benchmark_indices` | `fact_benchmark_indices` | 8,050 | 8,050 | True |

## Notes

- The raw NAV file is trading-day grain. The processed NAV table is calendar-day grain because the rubric asks for weekend/holiday forward fill.
- `04_monthly_sip_inflows.csv` has null YoY growth for the first 12 months because no prior-year baseline exists.
- SQLite row counts are verified against processed outputs, not raw NAV, because NAV receives an intentional calendar expansion.
