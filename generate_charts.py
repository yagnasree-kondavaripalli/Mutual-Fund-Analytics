"""Export chart PNGs and interactive Plotly HTML charts for the final report."""

from __future__ import annotations

import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns

from config import CHARTS_DIR, PROCESSED_DIR, REPORTS_DIR, ensure_project_dirs

sns.set_theme(style="whitegrid", palette=["#0B3D5C", "#00866E", "#F2A541", "#8D6CAB", "#D1495B", "#4C78A8"])


def savefig(name: str) -> None:
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / name, dpi=170, bbox_inches="tight")
    plt.close()


def load_data() -> dict[str, pd.DataFrame]:
    return {
        "fund": pd.read_csv(PROCESSED_DIR / "fund_master.csv"),
        "nav": pd.read_csv(PROCESSED_DIR / "nav_history.csv", parse_dates=["date"]),
        "aum": pd.read_csv(PROCESSED_DIR / "aum_by_fund_house.csv", parse_dates=["date"]),
        "sip": pd.read_csv(PROCESSED_DIR / "monthly_sip_inflows.csv", parse_dates=["month"]),
        "cat": pd.read_csv(PROCESSED_DIR / "category_inflows.csv", parse_dates=["month"]),
        "folio": pd.read_csv(PROCESSED_DIR / "industry_folio_count.csv", parse_dates=["month"]),
        "perf": pd.read_csv(PROCESSED_DIR / "scheme_performance.csv"),
        "txn": pd.read_csv(PROCESSED_DIR / "investor_transactions.csv", parse_dates=["transaction_date"]),
        "hold": pd.read_csv(PROCESSED_DIR / "portfolio_holdings.csv", parse_dates=["portfolio_date"]),
        "bench": pd.read_csv(PROCESSED_DIR / "benchmark_indices.csv", parse_dates=["date"]),
        "returns": pd.read_csv(PROCESSED_DIR / "daily_returns.csv", parse_dates=["date"]),
        "score": pd.read_csv(REPORTS_DIR / "fund_scorecard.csv"),
        "var": pd.read_csv(REPORTS_DIR / "var_cvar_report.csv"),
    }


def nav_trends(data: dict[str, pd.DataFrame]) -> None:
    nav = data["nav"].merge(data["fund"][["amfi_code", "scheme_name"]], on="amfi_code", how="left")
    raw_nav = nav[~nav["is_forward_filled"].astype(bool)]
    plt.figure(figsize=(13, 7))
    for _, group in raw_nav.groupby("scheme_name"):
        plt.plot(group["date"], group["nav"], linewidth=0.7, alpha=0.45)
    plt.axvspan(pd.Timestamp("2023-04-01"), pd.Timestamp("2023-12-31"), color="#00866E", alpha=0.09, label="2023 bull run")
    plt.axvspan(pd.Timestamp("2024-03-01"), pd.Timestamp("2024-06-30"), color="#D1495B", alpha=0.09, label="2024 corrections")
    plt.title("Daily NAV Trends Across 40 Schemes")
    plt.ylabel("NAV")
    plt.legend()
    savefig("01_nav_trends_all_schemes.png")

    fig = px.line(
        raw_nav,
        x="date",
        y="nav",
        color="scheme_name",
        title="Interactive Daily NAV Trends - 40 Schemes",
    )
    fig.add_vrect(x0="2023-04-01", x1="2023-12-31", fillcolor="green", opacity=0.08, line_width=0)
    fig.add_vrect(x0="2024-03-01", x1="2024-06-30", fillcolor="red", opacity=0.08, line_width=0)
    fig.write_html(CHARTS_DIR / "01_nav_trends_all_schemes_plotly.html")


def aum_chart(data: dict[str, pd.DataFrame]) -> None:
    aum = data["aum"].copy()
    aum["year"] = aum["date"].dt.year
    yearly = aum.sort_values("date").groupby(["year", "fund_house"], as_index=False).tail(1)
    plt.figure(figsize=(13, 7))
    sns.barplot(data=yearly, x="fund_house", y="aum_lakh_crore", hue="year")
    plt.title("AUM Growth by Fund House, Year-End 2022-2025")
    plt.ylabel("AUM (Lakh Crore INR)")
    plt.xlabel("")
    plt.xticks(rotation=35, ha="right")
    sbi_latest = yearly[yearly["fund_house"].str.contains("SBI", case=False, na=False)].sort_values("date").tail(1)
    if not sbi_latest.empty:
        row = sbi_latest.iloc[0]
        plt.annotate(
            f"SBI dominance: {row['aum_lakh_crore']:.2f}L Cr",
            xy=(0, row["aum_lakh_crore"]),
            xytext=(0.5, row["aum_lakh_crore"] + 0.8),
            arrowprops={"arrowstyle": "->", "color": "#D1495B"},
            color="#D1495B",
            fontsize=10,
        )
    savefig("02_aum_growth_by_fund_house.png")


def sip_chart(data: dict[str, pd.DataFrame]) -> None:
    sip = data["sip"]
    peak = sip.loc[sip["sip_inflow_crore"].idxmax()]
    plt.figure(figsize=(12, 6))
    plt.plot(sip["month"], sip["sip_inflow_crore"], marker="o", linewidth=2.2, color="#0B3D5C")
    plt.scatter([peak["month"]], [peak["sip_inflow_crore"]], color="#D1495B", s=80, zorder=5)
    plt.annotate(
        f"All-time high: Rs {peak['sip_inflow_crore']:,.0f} Cr",
        xy=(peak["month"], peak["sip_inflow_crore"]),
        xytext=(peak["month"] - pd.DateOffset(months=12), peak["sip_inflow_crore"] * 0.95),
        arrowprops={"arrowstyle": "->", "color": "#D1495B"},
        color="#D1495B",
    )
    plt.title("Monthly SIP Inflows, Jan 2022-Dec 2025")
    plt.ylabel("SIP Inflow (Crore INR)")
    savefig("03_sip_inflow_time_series.png")

    fig = px.line(sip, x="month", y="sip_inflow_crore", markers=True, title="Interactive Monthly SIP Inflow Trend")
    fig.add_annotation(x=peak["month"], y=peak["sip_inflow_crore"], text=f"Rs {peak['sip_inflow_crore']:,.0f} Cr", showarrow=True)
    fig.write_html(CHARTS_DIR / "03_sip_inflow_time_series_plotly.html")


def category_heatmap(data: dict[str, pd.DataFrame]) -> None:
    pivot = data["cat"].assign(month_label=lambda x: x["month"].dt.strftime("%b-%y")).pivot(index="category", columns="month_label", values="net_inflow_crore")
    plt.figure(figsize=(13, 7))
    sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.25)
    plt.title("Category Net Inflow Heatmap")
    plt.xlabel("Month")
    plt.ylabel("Fund Category")
    savefig("04_category_inflow_heatmap.png")


def investor_charts(data: dict[str, pd.DataFrame]) -> None:
    txn = data["txn"]
    sip = txn[txn["transaction_type"] == "SIP"]
    plt.figure(figsize=(8, 8))
    txn["age_group"].value_counts().sort_index().plot.pie(autopct="%1.1f%%", startangle=90, colors=sns.color_palette("Set2"))
    plt.ylabel("")
    plt.title("Investor Age Group Distribution")
    savefig("05_age_group_distribution_pie.png")

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=sip, x="age_group", y="amount_inr", showfliers=False)
    plt.title("SIP Amount Distribution by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("SIP Amount (INR)")
    savefig("06_sip_amount_box_by_age.png")

    plt.figure(figsize=(7, 7))
    txn["gender"].value_counts().plot.pie(autopct="%1.1f%%", startangle=90, colors=["#0B3D5C", "#F2A541", "#8D6CAB"])
    plt.ylabel("")
    plt.title("Investor Gender Split")
    savefig("07_gender_split.png")

    state = sip.groupby("state", as_index=False)["amount_inr"].sum().sort_values("amount_inr", ascending=True)
    plt.figure(figsize=(10, 7))
    sns.barplot(data=state, y="state", x="amount_inr", color="#00866E")
    plt.title("SIP Amount by State")
    plt.xlabel("SIP Amount (INR)")
    plt.ylabel("")
    savefig("08_sip_amount_by_state.png")

    plt.figure(figsize=(7, 7))
    sip["city_tier"].value_counts().plot.pie(autopct="%1.1f%%", startangle=90, colors=["#0B3D5C", "#00866E"])
    plt.ylabel("")
    plt.title("T30 vs B30 City-Tier SIP Split")
    savefig("09_city_tier_pie.png")

    monthly = txn.assign(month=lambda x: x["transaction_date"].dt.to_period("M").dt.to_timestamp()).groupby(["month", "transaction_type"], as_index=False).size()
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly, x="month", y="size", hue="transaction_type", marker="o")
    plt.title("Monthly Transaction Volume by Type")
    plt.ylabel("Transactions")
    savefig("10_monthly_transaction_volume.png")

    plt.figure(figsize=(7, 7))
    txn["transaction_type"].value_counts().plot.pie(autopct="%1.1f%%", startangle=90, colors=sns.color_palette("Set3"))
    plt.ylabel("")
    plt.title("Transaction Type Mix")
    savefig("11_transaction_type_mix.png")


def folio_chart(data: dict[str, pd.DataFrame]) -> None:
    folio = data["folio"]
    plt.figure(figsize=(12, 6))
    plt.plot(folio["month"], folio["total_folios_crore"], marker="o", linewidth=2.2, color="#0B3D5C")
    first = folio.iloc[0]
    last = folio.iloc[-1]
    for row in [first, last]:
        plt.annotate(f"{row['total_folios_crore']:.2f} Cr", xy=(row["month"], row["total_folios_crore"]), xytext=(row["month"], row["total_folios_crore"] + 0.7))
    plt.title("Industry Folio Count Growth")
    plt.ylabel("Total Folios (Crore)")
    savefig("12_folio_count_growth.png")


def return_correlation(data: dict[str, pd.DataFrame]) -> None:
    returns = data["returns"]
    selected = data["score"].head(10)["amfi_code"].tolist()
    pivot = returns[returns["amfi_code"].isin(selected)].pivot(index="date", columns="amfi_code", values="daily_return")
    corr = pivot.corr()
    label_map = data["fund"].set_index("amfi_code")["scheme_name"].to_dict()
    corr.index = [label_map.get(i, i)[:24] for i in corr.index]
    corr.columns = [label_map.get(i, i)[:24] for i in corr.columns]
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, cmap="vlag", center=0, annot=False)
    plt.title("Daily Return Correlation - Top 10 Scorecard Funds")
    savefig("13_nav_return_correlation_heatmap.png")


def sector_donut(data: dict[str, pd.DataFrame]) -> None:
    sector = data["hold"].groupby("sector", as_index=False)["weight_pct"].sum().sort_values("weight_pct", ascending=False)
    plt.figure(figsize=(8, 8))
    wedges, _ = plt.pie(sector["weight_pct"], startangle=90, colors=sns.color_palette("tab20", len(sector)))
    centre = plt.Circle((0, 0), 0.58, fc="white")
    fig = plt.gcf()
    fig.gca().add_artist(centre)
    plt.legend(wedges, sector["sector"], title="Sector", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=8)
    plt.title("Aggregate Sector Allocation Across Equity Holdings")
    savefig("14_sector_allocation_donut.png")


def performance_charts(data: dict[str, pd.DataFrame]) -> None:
    perf = data["perf"]
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=perf, x="return_3yr_pct", y="std_dev_ann_pct", size="aum_crore", hue="risk_grade", sizes=(40, 600), alpha=0.72)
    plt.title("Risk-Return Scatter: 3Y Return vs Annualized Std Dev")
    plt.xlabel("3Y Return (%)")
    plt.ylabel("Annualized Std Dev (%)")
    savefig("15_fund_risk_return_scatter.png")

    top_sharpe = data["score"].sort_values("sharpe_ratio", ascending=False).head(10).sort_values("sharpe_ratio")
    plt.figure(figsize=(10, 6))
    sns.barplot(data=top_sharpe, x="sharpe_ratio", y="scheme_name", color="#00866E")
    plt.title("Top 10 Funds by Computed Sharpe Ratio")
    plt.xlabel("Sharpe Ratio")
    plt.ylabel("")
    savefig("16_top_funds_by_sharpe.png")

    worst_dd = data["score"].sort_values("max_drawdown").head(10).sort_values("max_drawdown", ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=worst_dd, x="max_drawdown", y="scheme_name", color="#D1495B")
    plt.title("Worst Maximum Drawdowns")
    plt.xlabel("Max Drawdown")
    plt.ylabel("")
    savefig("17_max_drawdown_bar.png")

    var = data["var"].sort_values("var_95").head(10).sort_values("var_95", ascending=False)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=var, x="var_95", y="scheme_name", color="#8D6CAB")
    plt.title("Highest Historical 95% VaR by Fund")
    plt.xlabel("Daily VaR 95%")
    plt.ylabel("")
    savefig("18_var_95_bar.png")


def benchmark_dual_axis(data: dict[str, pd.DataFrame]) -> None:
    sip = data["sip"].set_index("month")["sip_inflow_crore"]
    nifty = data["bench"][data["bench"]["index_name"] == "NIFTY50"].set_index("date")["close_value"].resample("MS").last()
    joined = pd.concat([sip, nifty], axis=1).dropna()
    joined.columns = ["sip_inflow_crore", "nifty50"]
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.bar(joined.index, joined["sip_inflow_crore"], width=22, color="#0B3D5C", alpha=0.72, label="SIP inflow")
    ax1.set_ylabel("SIP Inflow (Crore INR)")
    ax2 = ax1.twinx()
    ax2.plot(joined.index, joined["nifty50"], color="#F2A541", linewidth=2.2, label="NIFTY50")
    ax2.set_ylabel("NIFTY50 Close")
    plt.title("SIP Inflows and NIFTY50 Trend")
    fig.tight_layout()
    plt.savefig(CHARTS_DIR / "19_sip_vs_nifty50_dual_axis.png", dpi=170, bbox_inches="tight")
    plt.close()


def main() -> None:
    ensure_project_dirs()
    data = load_data()
    nav_trends(data)
    aum_chart(data)
    sip_chart(data)
    category_heatmap(data)
    investor_charts(data)
    folio_chart(data)
    return_correlation(data)
    sector_donut(data)
    performance_charts(data)
    benchmark_dual_axis(data)
    print(f"Wrote chart PNG/HTML files to {CHARTS_DIR}")


if __name__ == "__main__":
    main()
