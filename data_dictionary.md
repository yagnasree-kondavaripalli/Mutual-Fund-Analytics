# Data Dictionary

## fund_master

| Column | Type | Business Definition |
| --- | --- | --- |
| `amfi_code` | `int64` | AMFI scheme code used as the scheme identifier. |
| `fund_house` | `string` | Source-provided field; see raw CSV and project context. |
| `scheme_name` | `string` | Source-provided field; see raw CSV and project context. |
| `category` | `string` | Source-provided field; see raw CSV and project context. |
| `sub_category` | `string` | Source-provided field; see raw CSV and project context. |
| `plan` | `string` | Source-provided field; see raw CSV and project context. |
| `launch_date` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `benchmark` | `string` | Source-provided field; see raw CSV and project context. |
| `expense_ratio_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `exit_load_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `min_sip_amount` | `int64` | Source-provided field; see raw CSV and project context. |
| `min_lumpsum_amount` | `int64` | Source-provided field; see raw CSV and project context. |
| `fund_manager` | `string` | Source-provided field; see raw CSV and project context. |
| `risk_category` | `string` | Fund risk category from fund master. |
| `sebi_category_code` | `string` | Source-provided field; see raw CSV and project context. |

## nav_history

| Column | Type | Business Definition |
| --- | --- | --- |
| `amfi_code` | `int64` | AMFI scheme code used as the scheme identifier. |
| `date` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `nav` | `float64` | Net Asset Value per unit. |
| `is_forward_filled` | `bool` | Source-provided field; see raw CSV and project context. |

## aum_by_fund_house

| Column | Type | Business Definition |
| --- | --- | --- |
| `date` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `fund_house` | `string` | Source-provided field; see raw CSV and project context. |
| `aum_lakh_crore` | `float64` | Assets under management in lakh crore INR. |
| `aum_crore` | `int64` | Assets under management in crore INR. |
| `num_schemes` | `int64` | Source-provided field; see raw CSV and project context. |

## monthly_sip_inflows

| Column | Type | Business Definition |
| --- | --- | --- |
| `month` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `sip_inflow_crore` | `int64` | Monthly SIP inflow in crore INR. |
| `active_sip_accounts_crore` | `float64` | Source-provided field; see raw CSV and project context. |
| `new_sip_accounts_lakh` | `float64` | Source-provided field; see raw CSV and project context. |
| `sip_aum_lakh_crore` | `float64` | Source-provided field; see raw CSV and project context. |
| `yoy_growth_pct` | `float64` | Source-provided field; see raw CSV and project context. |

## category_inflows

| Column | Type | Business Definition |
| --- | --- | --- |
| `month` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `category` | `string` | Source-provided field; see raw CSV and project context. |
| `net_inflow_crore` | `float64` | Source-provided field; see raw CSV and project context. |

## industry_folio_count

| Column | Type | Business Definition |
| --- | --- | --- |
| `month` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `total_folios_crore` | `float64` | Source-provided field; see raw CSV and project context. |
| `equity_folios_crore` | `float64` | Source-provided field; see raw CSV and project context. |
| `debt_folios_crore` | `float64` | Source-provided field; see raw CSV and project context. |
| `hybrid_folios_crore` | `float64` | Source-provided field; see raw CSV and project context. |
| `others_folios_crore` | `float64` | Source-provided field; see raw CSV and project context. |

## scheme_performance

| Column | Type | Business Definition |
| --- | --- | --- |
| `amfi_code` | `int64` | AMFI scheme code used as the scheme identifier. |
| `scheme_name` | `string` | Source-provided field; see raw CSV and project context. |
| `fund_house` | `string` | Source-provided field; see raw CSV and project context. |
| `category` | `string` | Source-provided field; see raw CSV and project context. |
| `plan` | `string` | Source-provided field; see raw CSV and project context. |
| `return_1yr_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `return_3yr_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `return_5yr_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `benchmark_3yr_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `alpha` | `float64` | Source-provided field; see raw CSV and project context. |
| `beta` | `float64` | Source-provided field; see raw CSV and project context. |
| `sharpe_ratio` | `float64` | Source-provided field; see raw CSV and project context. |
| `sortino_ratio` | `float64` | Source-provided field; see raw CSV and project context. |
| `std_dev_ann_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `max_drawdown_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `aum_crore` | `int64` | Assets under management in crore INR. |
| `expense_ratio_pct` | `float64` | Source-provided field; see raw CSV and project context. |
| `morningstar_rating` | `int64` | Source-provided field; see raw CSV and project context. |
| `risk_grade` | `string` | Scheme risk grade from performance file. |

## investor_transactions

| Column | Type | Business Definition |
| --- | --- | --- |
| `transaction_id` | `int64` | Source-provided field; see raw CSV and project context. |
| `investor_id` | `string` | Source-provided field; see raw CSV and project context. |
| `transaction_date` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `amfi_code` | `int64` | AMFI scheme code used as the scheme identifier. |
| `transaction_type` | `str` | Source-provided field; see raw CSV and project context. |
| `amount_inr` | `int64` | Investor transaction amount in INR. |
| `state` | `string` | Source-provided field; see raw CSV and project context. |
| `city` | `string` | Source-provided field; see raw CSV and project context. |
| `city_tier` | `string` | Source-provided field; see raw CSV and project context. |
| `age_group` | `string` | Source-provided field; see raw CSV and project context. |
| `gender` | `string` | Source-provided field; see raw CSV and project context. |
| `annual_income_lakh` | `float64` | Source-provided field; see raw CSV and project context. |
| `payment_mode` | `string` | Source-provided field; see raw CSV and project context. |
| `kyc_status` | `string` | Source-provided field; see raw CSV and project context. |

## portfolio_holdings

| Column | Type | Business Definition |
| --- | --- | --- |
| `amfi_code` | `int64` | AMFI scheme code used as the scheme identifier. |
| `stock_symbol` | `string` | Source-provided field; see raw CSV and project context. |
| `stock_name` | `string` | Source-provided field; see raw CSV and project context. |
| `sector` | `string` | Source-provided field; see raw CSV and project context. |
| `weight_pct` | `float64` | Portfolio holding weight as a percentage of fund assets. |
| `market_value_cr` | `float64` | Source-provided field; see raw CSV and project context. |
| `current_price_inr` | `float64` | Source-provided field; see raw CSV and project context. |
| `portfolio_date` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |

## benchmark_indices

| Column | Type | Business Definition |
| --- | --- | --- |
| `date` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `index_name` | `string` | Source-provided field; see raw CSV and project context. |
| `close_value` | `float64` | Benchmark index close value. |

## dim_investor

| Column | Type | Business Definition |
| --- | --- | --- |
| `investor_id` | `string` | Source-provided field; see raw CSV and project context. |
| `state` | `string` | Source-provided field; see raw CSV and project context. |
| `city` | `string` | Source-provided field; see raw CSV and project context. |
| `city_tier` | `string` | Source-provided field; see raw CSV and project context. |
| `age_group` | `string` | Source-provided field; see raw CSV and project context. |
| `gender` | `string` | Source-provided field; see raw CSV and project context. |
| `annual_income_lakh` | `float64` | Source-provided field; see raw CSV and project context. |
| `kyc_status` | `string` | Source-provided field; see raw CSV and project context. |

## dim_date

| Column | Type | Business Definition |
| --- | --- | --- |
| `date` | `datetime64[us]` | Source-provided field; see raw CSV and project context. |
| `date_key` | `int64` | Source-provided field; see raw CSV and project context. |
| `year` | `int32` | Source-provided field; see raw CSV and project context. |
| `quarter` | `int32` | Source-provided field; see raw CSV and project context. |
| `month` | `int32` | Source-provided field; see raw CSV and project context. |
| `month_name` | `str` | Source-provided field; see raw CSV and project context. |
| `day_of_week` | `str` | Source-provided field; see raw CSV and project context. |
| `is_weekend` | `bool` | Source-provided field; see raw CSV and project context. |
| `fiscal_year` | `int32` | Source-provided field; see raw CSV and project context. |
| `fiscal_quarter` | `int32` | Source-provided field; see raw CSV and project context. |
