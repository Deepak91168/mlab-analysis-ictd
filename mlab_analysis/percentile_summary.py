#!/usr/bin/env python3
"""Write download and upload percentile tables from cleaned M-Lab CSVs."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT_DIR = (
    PROJECT_ROOT / "outputs" / "analysis" / "2026-06-18_to_2026-11-04"
)
DEFAULT_OUTPUT_DIR = DEFAULT_INPUT_DIR / "percentiles"

THROUGHPUT_PERCENTILES = (1, 5, 10, 15, 20, 25, 50)
TAIL_PERCENTILES = (50, 75, 80, 85, 90, 95, 99)
TABLE_COLUMNS = [
    "metric",
    "source_column",
    "unit",
    "n",
    "missing_or_invalid",
    "mean",
    "median",
    "std",
    *(f"p{p}" for p in sorted(set(THROUGHPUT_PERCENTILES + TAIL_PERCENTILES))),
    "status",
]

METRICS = {
    "download": (
        ("Download throughput", "download_mbps", "Mbps", THROUGHPUT_PERCENTILES),
        ("Minimum RTT", "min_rtt_ms", "ms", TAIL_PERCENTILES),
        ("Packet loss", "loss_percent", "%", TAIL_PERCENTILES),
    ),
    "upload": (
        ("Upload throughput", "upload_mbps", "Mbps", THROUGHPUT_PERCENTILES),
        ("Minimum RTT", "min_rtt_ms", "ms", TAIL_PERCENTILES),
        ("Packet loss", "loss_percent", "%", TAIL_PERCENTILES),
    ),
}


def summarize_metric(
    frame: pd.DataFrame,
    metric: str,
    column: str,
    unit: str,
    percentiles: tuple[int, ...],
) -> dict:
    record = {
        "metric": metric,
        "source_column": column,
        "unit": unit,
        "n": 0,
        "missing_or_invalid": len(frame),
        "mean": np.nan,
        "median": np.nan,
        "std": np.nan,
        "status": "source column is unavailable",
    }
    record.update({f"p{p}": np.nan for p in set(THROUGHPUT_PERCENTILES + TAIL_PERCENTILES)})

    if column not in frame.columns:
        return record

    numeric = pd.to_numeric(frame[column], errors="coerce")
    finite = numeric[np.isfinite(numeric)]
    record["n"] = int(finite.size)
    record["missing_or_invalid"] = int(len(frame) - finite.size)
    if finite.empty:
        record["status"] = "no finite numeric values"
        return record

    record["mean"] = finite.mean()
    record["median"] = finite.median()
    record["std"] = finite.std(ddof=1)
    for percentile in percentiles:
        record[f"p{percentile}"] = finite.quantile(percentile / 100)
    record["status"] = "ok"
    return record


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create separate throughput, RTT, and packet-loss percentile tables."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help=f"Folder containing download_clean.csv and upload_clean.csv (default: {DEFAULT_INPUT_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Folder for the two output CSV tables (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for direction, metrics in METRICS.items():
        input_path = args.input_dir / f"{direction}_clean.csv"
        if not input_path.is_file():
            raise FileNotFoundError(f"Cleaned input CSV not found: {input_path}")

        frame = pd.read_csv(input_path, low_memory=False)
        rows = [
            summarize_metric(frame, metric, column, unit, percentiles)
            for metric, column, unit, percentiles in metrics
        ]
        table = pd.DataFrame(rows, columns=TABLE_COLUMNS)
        output_path = args.output_dir / f"{direction}_percentiles.csv"
        table.to_csv(output_path, index=False, float_format="%.6f")

        print(f"\n{direction.title()} — {len(frame):,} cleaned rows")
        print(table.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
        print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
