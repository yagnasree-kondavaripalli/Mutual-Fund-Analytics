"""Load and profile the raw Bluestock mutual fund datasets."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from config import DOCS_DIR, RAW_DIR, RAW_FILES, ensure_project_dirs


@dataclass(frozen=True)
class DatasetProfile:
    name: str
    rows: int
    columns: int
    duplicate_rows: int
    null_columns: dict[str, int]
    date_ranges: dict[str, str]


def load_raw_datasets(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """Load all expected raw CSVs into a dictionary keyed by dataset name."""
    datasets: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    for name, filename in RAW_FILES.items():
        path = raw_dir / filename
        if not path.exists():
            missing.append(filename)
            continue
        datasets[name] = pd.read_csv(path)
    if missing:
        raise FileNotFoundError(f"Missing raw file(s): {', '.join(missing)}")
    return datasets


def _date_ranges(df: pd.DataFrame) -> dict[str, str]:
    ranges: dict[str, str] = {}
    for column in df.columns:
        lower = column.lower()
        if not any(token in lower for token in ["date", "month", "quarter", "period"]):
            continue
        parsed = pd.to_datetime(df[column], errors="coerce")
        if parsed.notna().any():
            ranges[column] = f"{parsed.min().date()} to {parsed.max().date()}"
    return ranges


def profile_dataframe(name: str, df: pd.DataFrame) -> DatasetProfile:
    """Return compact profiling metadata for one dataframe."""
    null_columns = {col: int(count) for col, count in df.isna().sum().items() if count}
    return DatasetProfile(
        name=name,
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        duplicate_rows=int(df.duplicated().sum()),
        null_columns=null_columns,
        date_ranges=_date_ranges(df),
    )


def validate_amfi_codes(datasets: dict[str, pd.DataFrame]) -> dict[str, object]:
    """Validate that fund master AMFI codes are represented in NAV history."""
    fund_codes = set(datasets["fund_master"]["amfi_code"].astype(int))
    nav_codes = set(datasets["nav_history"]["amfi_code"].astype(int))
    nav_counts = datasets["nav_history"].groupby("amfi_code").size()
    return {
        "fund_master_codes": len(fund_codes),
        "nav_history_codes": len(nav_codes),
        "missing_in_nav_history": sorted(fund_codes - nav_codes),
        "extra_in_nav_history": sorted(nav_codes - fund_codes),
        "min_nav_rows_per_scheme": int(nav_counts.min()),
        "max_nav_rows_per_scheme": int(nav_counts.max()),
    }


def write_ingestion_profile(datasets: dict[str, pd.DataFrame]) -> Path:
    """Write a Markdown profile with shape, dtypes, head, and anomalies."""
    ensure_project_dirs()
    path = DOCS_DIR / "ingestion_profile.md"
    lines = ["# Raw Data Ingestion Profile", ""]
    for name, df in datasets.items():
        profile = profile_dataframe(name, df)
        lines.extend(
            [
                f"## {name}",
                "",
                f"- Shape: `{profile.rows:,}` rows x `{profile.columns}` columns",
                f"- Duplicate rows: `{profile.duplicate_rows}`",
                f"- Null columns: `{profile.null_columns or 'none'}`",
                f"- Date ranges: `{profile.date_ranges or 'none detected'}`",
                "",
                "### Dtypes",
                "",
                "```text",
                df.dtypes.to_string(),
                "```",
                "",
                "### Head",
                "",
                "```text",
                df.head().to_string(index=False),
                "```",
                "",
            ]
        )
    amfi = validate_amfi_codes(datasets)
    lines.extend(["## AMFI Code Validation", "", "```text", str(amfi), "```", ""])
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    """Print and persist a first-pass profile for the raw datasets."""
    datasets = load_raw_datasets()
    for name, df in datasets.items():
        profile = profile_dataframe(name, df)
        print(f"\n{name}: {profile.rows:,} rows x {profile.columns} columns")
        print(df.dtypes)
        print(df.head())
        if profile.null_columns:
            print("Null columns:", profile.null_columns)
        if profile.duplicate_rows:
            print("Duplicate rows:", profile.duplicate_rows)
    print("\nAMFI validation:", validate_amfi_codes(datasets))
    print(f"\nWrote {write_ingestion_profile(datasets)}")


if __name__ == "__main__":
    main()

