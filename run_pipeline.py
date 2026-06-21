"""Master runner for the Bluestock mutual fund analytics capstone."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

STEPS = [
    ("Profile raw datasets", ROOT / "scripts" / "data_ingestion.py"),
    ("Clean data and load SQLite", ROOT / "scripts" / "etl_pipeline.py"),
    ("Compute performance/risk metrics", ROOT / "scripts" / "compute_metrics.py"),
    ("Generate report charts", ROOT / "scripts" / "generate_charts.py"),
    ("Generate notebooks and report starters", ROOT / "scripts" / "create_notebooks.py"),
]


def run_step(label: str, script: Path) -> None:
    print(f"\n=== {label} ===")
    subprocess.run([PYTHON, str(script)], cwd=ROOT, check=True)


def main() -> None:
    for label, script in STEPS:
        run_step(label, script)
    print("\nPipeline complete. Review reports/, notebooks/, docs/, and data/processed/.")


if __name__ == "__main__":
    main()

