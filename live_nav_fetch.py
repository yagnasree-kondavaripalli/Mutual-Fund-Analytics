"""Fetch live NAV data from mfapi.in and save it as raw CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import requests

from config import LIVE_NAV_SCHEMES, RAW_DIR, ensure_project_dirs

MFAPI_URL = "https://api.mfapi.in/mf/{scheme_code}"


def fetch_scheme_nav(scheme_code: int, timeout: int = 30) -> pd.DataFrame:
    """Fetch NAV history for one mfapi.in scheme code."""
    response = requests.get(MFAPI_URL.format(scheme_code=scheme_code), timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("data", [])
    if not rows:
        raise ValueError(f"mfapi.in returned no NAV rows for scheme {scheme_code}")
    df = pd.DataFrame(rows)
    df["scheme_code"] = int(scheme_code)
    df["scheme_name"] = payload.get("meta", {}).get("scheme_name")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["date", "nav"]).sort_values("date")
    return df[["scheme_code", "scheme_name", "date", "nav"]]


def fetch_many(schemes: dict[int, str] | None = None, output_dir: Path = RAW_DIR) -> list[Path]:
    """Fetch multiple scheme NAV histories and return saved CSV paths."""
    ensure_project_dirs()
    schemes = schemes or LIVE_NAV_SCHEMES
    saved: list[Path] = []
    for scheme_code, label in schemes.items():
        df = fetch_scheme_nav(scheme_code)
        safe_label = label.lower().replace(" ", "_").replace("/", "_")
        path = output_dir / f"live_nav_{scheme_code}_{safe_label}.csv"
        df.to_csv(path, index=False)
        saved.append(path)
        print(f"Saved {path} ({len(df):,} rows)")
    combined = pd.concat([pd.read_csv(path) for path in saved], ignore_index=True)
    combined_path = output_dir / "live_nav_key_schemes.csv"
    combined.to_csv(combined_path, index=False)
    saved.append(combined_path)
    print(f"Saved {combined_path} ({len(combined):,} rows)")
    return saved


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scheme-code",
        type=int,
        action="append",
        help="Optional mfapi.in scheme code. Repeat for multiple codes. Defaults to the project key schemes.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.scheme_code:
        schemes = {code: f"scheme_{code}" for code in args.scheme_code}
    else:
        schemes = LIVE_NAV_SCHEMES
    fetch_many(schemes)


if __name__ == "__main__":
    main()

