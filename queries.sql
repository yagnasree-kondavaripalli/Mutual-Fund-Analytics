-- Q1. Top 5 funds by latest scheme-level AUM
SELECT scheme_name, fund_house, category, plan, aum_crore
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;

-- Q2. Average NAV per month by fund
SELECT f.scheme_name, substr(n.date, 1, 7) AS month, ROUND(AVG(n.nav), 2) AS avg_nav
FROM fact_nav n
JOIN dim_fund f ON f.amfi_code = n.amfi_code
GROUP BY f.scheme_name, substr(n.date, 1, 7)
ORDER BY month, f.scheme_name;

-- Q3. SIP year-on-year growth by month
SELECT month, sip_inflow_crore, yoy_growth_pct
FROM fact_sip
ORDER BY month;

-- Q4. Transaction amount and count by state
SELECT state, COUNT(*) AS txns, ROUND(SUM(amount_inr) / 10000000.0, 2) AS amount_cr
FROM fact_transactions
GROUP BY state
ORDER BY amount_cr DESC;

-- Q5. Funds with expense ratio below 1%
SELECT scheme_name, fund_house, plan, expense_ratio_pct, risk_grade
FROM fact_performance
WHERE expense_ratio_pct < 1
ORDER BY expense_ratio_pct ASC;

-- Q6. Top fund houses by Dec 2025 AUM
SELECT fund_house, aum_lakh_crore, aum_crore, num_schemes
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC;

-- Q7. Top categories by FY25 net inflow
SELECT category, ROUND(SUM(net_inflow_crore), 2) AS fy25_net_inflow_cr
FROM fact_category_inflows
GROUP BY category
ORDER BY fy25_net_inflow_cr DESC;

-- Q8. SIP investor demographics by age group
SELECT age_group, COUNT(*) AS sip_txns, ROUND(AVG(amount_inr), 2) AS avg_sip_amount
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY age_group
ORDER BY avg_sip_amount DESC;

-- Q9. Sector exposure across portfolio holdings
SELECT sector, ROUND(SUM(weight_pct), 2) AS total_weight_pct, ROUND(SUM(market_value_cr), 2) AS market_value_cr
FROM fact_portfolio_holdings
GROUP BY sector
ORDER BY total_weight_pct DESC;

-- Q10. Benchmark index returns over full available period
WITH endpoints AS (
    SELECT
        index_name,
        FIRST_VALUE(close_value) OVER (PARTITION BY index_name ORDER BY date) AS start_value,
        FIRST_VALUE(close_value) OVER (PARTITION BY index_name ORDER BY date DESC) AS end_value
    FROM fact_benchmark_indices
)
SELECT DISTINCT index_name, ROUND((end_value / start_value - 1) * 100, 2) AS total_return_pct
FROM endpoints
ORDER BY total_return_pct DESC;
