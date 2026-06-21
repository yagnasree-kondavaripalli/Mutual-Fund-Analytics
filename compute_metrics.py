"""Compute fund performance, risk, benchmark, and portfolio concentration outputs."""

from __future__ import annotations

import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from config import CHARTS_DIR, PROCESSED_DIR, REPORTS_DIR, RISK_FREE_RATE_ANNUAL, ensure_project_dirs


def _load_processed() -> dict[str, pd.DataFrame]:
    return {
        "fund": pd.read_csv(PROCESSED_DIR / "fund_master.csv", parse_dates=["launch_date"]),
        "nav": pd.read_csv(PROCESSED_DIR / "nav_history.csv", parse_dates=["date"]),
        "bench": pd.read_csv(PROCESSED_DIR / "benchmark_indices.csv", parse_dates=["date"]),
        "performance": pd.read_csv(PROCESSED_DIR / "scheme_performance.csv"),
        "holdings": pd.read_csv(PROCESSED_DIR / "portfolio_holdings.csv", parse_dates=["portfolio_date"]),
    }


def daily_returns(nav: pd.DataFrame) -> pd.DataFrame:
    wide = nav.pivot(index="date", columns="amfi_code", values="nav").sort_index()
    returns = wide.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan)
    long = returns.stack().rename("daily_return").reset_index()
    return long


def benchmark_returns(bench: pd.DataFrame) -> pd.DataFrame:
    wide = bench.pivot(index="date", columns="index_name", values="close_value").sort_index()
    return wide.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan)


def cagr_for_window(nav_series: pd.Series, years: int) -> float:
    series = nav_series.dropna()
    if series.empty:
        return np.nan
    end_date = series.index.max()
    start_cutoff = end_date - pd.DateOffset(years=years)
    window = series.loc[series.index >= start_cutoff]
    if len(window) < 2:
        return np.nan
    trading_years = (len(window) - 1) / 252
    if trading_years <= 0:
        return np.nan
    return (window.iloc[-1] / window.iloc[0]) ** (1 / trading_years) - 1


def max_drawdown(nav_series: pd.Series) -> tuple[float, pd.Timestamp | pd.NaT, pd.Timestamp | pd.NaT]:
    series = nav_series.dropna()
    if series.empty:
        return np.nan, pd.NaT, pd.NaT
    running_max = series.cummax()
    drawdown = series / running_max - 1
    trough = drawdown.idxmin()
    peak = series.loc[:trough].idxmax()
    return float(drawdown.loc[trough]), peak, trough


def compute_fund_metrics(data: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fund = data["fund"]
    nav = data["nav"]
    bench_returns = benchmark_returns(data["bench"])
    nav_wide = nav.pivot(index="date", columns="amfi_code", values="nav").sort_index()
    ret_wide = nav_wide.pct_change(fill_method=None)
    rf_daily = RISK_FREE_RATE_ANNUAL / 252

    rows = []
    alpha_beta_rows = []
    var_rows = []
    benchmark = bench_returns["NIFTY100"]
    for code in nav_wide.columns:
        nav_s = nav_wide[code].dropna()
        ret_s = ret_wide[code].dropna()
        if ret_s.empty:
            continue
        mean_excess = ret_s.mean() - rf_daily
        sharpe = mean_excess / ret_s.std() * math.sqrt(252) if ret_s.std() else np.nan
        downside = ret_s[ret_s < 0]
        sortino = mean_excess / downside.std() * math.sqrt(252) if downside.std() else np.nan
        var95 = ret_s.quantile(0.05)
        cvar95 = ret_s[ret_s <= var95].mean()
        max_dd, dd_start, dd_end = max_drawdown(nav_s)
        rows.append(
            {
                "amfi_code": code,
                "cagr_1yr": cagr_for_window(nav_s, 1),
                "cagr_3yr": cagr_for_window(nav_s, 3),
                "cagr_5yr": cagr_for_window(nav_s, 5),
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "max_drawdown": max_dd,
                "drawdown_start": dd_start,
                "drawdown_end": dd_end,
                "annualized_volatility": ret_s.std() * math.sqrt(252),
            }
        )
        var_rows.append({"amfi_code": code, "var_95": var95, "cvar_95": cvar95})
        aligned = pd.concat([ret_s.rename("fund"), benchmark.rename("benchmark")], axis=1, sort=True).dropna()
        if len(aligned) > 30:
            reg = stats.linregress(aligned["benchmark"], aligned["fund"])
            alpha_beta_rows.append(
                {
                    "amfi_code": code,
                    "benchmark": "NIFTY100",
                    "alpha_annualized": reg.intercept * 252,
                    "beta": reg.slope,
                    "r_squared": reg.rvalue**2,
                    "p_value": reg.pvalue,
                }
            )

    metrics = pd.DataFrame(rows).merge(fund[["amfi_code", "scheme_name", "fund_house", "category", "sub_category", "plan", "risk_category", "expense_ratio_pct"]], on="amfi_code", how="left")
    alpha_beta = pd.DataFrame(alpha_beta_rows).merge(fund[["amfi_code", "scheme_name", "fund_house"]], on="amfi_code", how="left")
    var_cvar = pd.DataFrame(var_rows).merge(fund[["amfi_code", "scheme_name", "fund_house", "risk_category"]], on="amfi_code", how="left")
    return metrics, alpha_beta, var_cvar


def compute_tracking_error(data: dict[str, pd.DataFrame], metrics: pd.DataFrame) -> pd.DataFrame:
    nav_returns = data["nav"].pivot(index="date", columns="amfi_code", values="nav").sort_index().pct_change(fill_method=None)
    bench_ret = benchmark_returns(data["bench"])
    top_codes = metrics.sort_values("sharpe_ratio", ascending=False).head(5)["amfi_code"].tolist()
    rows = []
    for code in top_codes:
        for index_name in ["NIFTY50", "NIFTY100"]:
            aligned = pd.concat([nav_returns[code].rename("fund"), bench_ret[index_name].rename("benchmark")], axis=1, sort=True).dropna()
            rows.append(
                {
                    "amfi_code": code,
                    "index_name": index_name,
                    "tracking_error": (aligned["fund"] - aligned["benchmark"]).std() * math.sqrt(252),
                }
            )
    return pd.DataFrame(rows).merge(data["fund"][["amfi_code", "scheme_name"]], on="amfi_code", how="left")


def compute_sector_hhi(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    holdings = data["holdings"].copy()
    sector_weights = holdings.groupby(["amfi_code", "sector"], as_index=False)["weight_pct"].sum()
    hhi = sector_weights.assign(weight_share=sector_weights["weight_pct"] / 100)
    hhi = hhi.groupby("amfi_code", as_index=False).agg(sector_hhi=("weight_share", lambda s: float((s**2).sum())))
    return hhi.merge(data["fund"][["amfi_code", "scheme_name", "fund_house", "category", "sub_category"]], on="amfi_code", how="left")


def build_scorecard(metrics: pd.DataFrame, alpha_beta: pd.DataFrame, performance: pd.DataFrame) -> pd.DataFrame:
    score = metrics.merge(alpha_beta[["amfi_code", "alpha_annualized", "beta"]], on="amfi_code", how="left")
    score = score.merge(performance[["amfi_code", "aum_crore", "morningstar_rating"]], on="amfi_code", how="left")
    score["return_rank"] = score["cagr_3yr"].rank(pct=True) * 100
    score["sharpe_rank"] = score["sharpe_ratio"].rank(pct=True) * 100
    score["alpha_rank"] = score["alpha_annualized"].rank(pct=True) * 100
    score["expense_rank_inverse"] = score["expense_ratio_pct"].rank(ascending=False, pct=True) * 100
    score["drawdown_rank_inverse"] = score["max_drawdown"].rank(pct=True) * 100
    score["fund_score"] = (
        0.30 * score["return_rank"]
        + 0.25 * score["sharpe_rank"]
        + 0.20 * score["alpha_rank"]
        + 0.15 * score["expense_rank_inverse"]
        + 0.10 * score["drawdown_rank_inverse"]
    )
    cols = [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "category",
        "sub_category",
        "plan",
        "risk_category",
        "fund_score",
        "cagr_1yr",
        "cagr_3yr",
        "cagr_5yr",
        "sharpe_ratio",
        "sortino_ratio",
        "alpha_annualized",
        "beta",
        "max_drawdown",
        "expense_ratio_pct",
        "aum_crore",
        "morningstar_rating",
    ]
    return score[cols].sort_values("fund_score", ascending=False)


def plot_rolling_sharpe(data: dict[str, pd.DataFrame]) -> None:
    nav = data["nav"]
    fund = data["fund"]
    key_codes = fund.head(5)["amfi_code"].tolist()
    nav_wide = nav[nav["amfi_code"].isin(key_codes)].pivot(index="date", columns="amfi_code", values="nav").sort_index()
    returns = nav_wide.pct_change(fill_method=None)
    rolling = returns.rolling(90).mean() / returns.rolling(90).std() * math.sqrt(252)
    labels = fund.set_index("amfi_code")["scheme_name"].to_dict()
    plt.figure(figsize=(12, 6))
    for code in key_codes:
        plt.plot(rolling.index, rolling[code], label=labels.get(code, code), linewidth=1.8)
    plt.axhline(0, color="#36454f", linewidth=0.8)
    plt.title("Rolling 90-Day Sharpe Ratio - Key Funds")
    plt.ylabel("Sharpe Ratio")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "rolling_sharpe_chart.png", dpi=160)
    plt.close()


def plot_benchmark_comparison(data: dict[str, pd.DataFrame], scorecard: pd.DataFrame) -> None:
    top_codes = scorecard.head(5)["amfi_code"].tolist()
    nav_wide = data["nav"][data["nav"]["amfi_code"].isin(top_codes)].pivot(index="date", columns="amfi_code", values="nav").sort_index()
    bench = data["bench"][data["bench"]["index_name"].isin(["NIFTY50", "NIFTY100"])].pivot(index="date", columns="index_name", values="close_value").sort_index()
    start = max(nav_wide.index.max() - pd.DateOffset(years=3), nav_wide.index.min())
    combined = pd.concat([nav_wide.loc[start:], bench.loc[start:]], axis=1).dropna(how="all")
    normalized = combined / combined.iloc[0] * 100
    labels = data["fund"].set_index("amfi_code")["scheme_name"].to_dict()
    plt.figure(figsize=(12, 7))
    for column in normalized.columns:
        label = labels.get(column, column)
        width = 2.4 if column in ["NIFTY50", "NIFTY100"] else 1.4
        plt.plot(normalized.index, normalized[column], label=label, linewidth=width)
    plt.title("Top 5 Fund Scorecard Schemes vs NIFTY50 and NIFTY100 - 3Y Indexed")
    plt.ylabel("Indexed Value (Start = 100)")
    plt.legend(fontsize=7, ncol=2)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "benchmark_comparison_chart.png", dpi=160)
    plt.close()


def main() -> None:
    ensure_project_dirs()
    data = _load_processed()
    returns = daily_returns(data["nav"])
    returns.to_csv(PROCESSED_DIR / "daily_returns.csv", index=False)
    metrics, alpha_beta, var_cvar = compute_fund_metrics(data)
    tracking = compute_tracking_error(data, metrics)
    sector_hhi = compute_sector_hhi(data)
    scorecard = build_scorecard(metrics, alpha_beta, data["performance"])

    metrics.to_csv(REPORTS_DIR / "fund_metrics_computed.csv", index=False)
    scorecard.to_csv(REPORTS_DIR / "fund_scorecard.csv", index=False)
    alpha_beta.to_csv(REPORTS_DIR / "alpha_beta.csv", index=False)
    var_cvar.to_csv(REPORTS_DIR / "var_cvar_report.csv", index=False)
    tracking.to_csv(REPORTS_DIR / "tracking_error.csv", index=False)
    sector_hhi.to_csv(REPORTS_DIR / "sector_hhi.csv", index=False)
    plot_rolling_sharpe(data)
    plot_benchmark_comparison(data, scorecard)
    print(f"Wrote metrics CSVs to {REPORTS_DIR}")
    print(f"Wrote metric charts to {CHARTS_DIR}")


if __name__ == "__main__":
    main()
