"""Simple risk-appetite fund recommender based on computed scorecard metrics."""

from __future__ import annotations

import argparse

import pandas as pd

from config import REPORTS_DIR

RISK_MAP = {
    "low": ["Low"],
    "moderate": ["Moderate", "Moderately High"],
    "high": ["High", "Very High"],
}


def recommend(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    """Return top funds for a Low, Moderate, or High risk appetite."""
    risk_key = risk_appetite.strip().lower()
    if risk_key not in RISK_MAP:
        raise ValueError("risk_appetite must be one of: Low, Moderate, High")
    scorecard = pd.read_csv(REPORTS_DIR / "fund_scorecard.csv")
    eligible = scorecard[scorecard["risk_category"].isin(RISK_MAP[risk_key])]
    columns = [
        "scheme_name",
        "fund_house",
        "risk_category",
        "fund_score",
        "cagr_3yr",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "expense_ratio_pct",
    ]
    return eligible.sort_values("fund_score", ascending=False).head(top_n)[columns]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--risk", default="Moderate", choices=["Low", "Moderate", "High"])
    parser.add_argument("--top-n", type=int, default=3)
    args = parser.parse_args()
    print(recommend(args.risk, args.top_n).to_string(index=False))


if __name__ == "__main__":
    main()

