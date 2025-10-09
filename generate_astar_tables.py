#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates CSV summary tables with mean metrics (d, g, #E, #F) for each heuristic using A*.

Input (files located in ./results):
  results/results_N3x3.csv
  results/results_5x5.csv
  results/results_7x7.csv
  results/results_9x9.csv

Output (saved to ./tables):
  tables/astar_table_3x3.csv
  tables/astar_table_5x5.csv
  tables/astar_table_7x7.csv
  tables/astar_table_9x9.csv
  tables/astar_table_all.csv   <- aggregated table including all map sizes
"""

import os
import glob
import pandas as pd

RESULTS_DIR = "results"
TABLES_DIR = "tables"
PATTERN = os.path.join(RESULTS_DIR, "results_*x*.csv")

METRICS = ["d", "g", "#E", "#F"]

# Preferred heuristic order for display
HEUR_ORDER = ["h", "h_chebyshev", "h_euclidean", "h_minhardness", "h_combined"]


def order_heuristics(index):
    """Return a sorted index prioritizing known heuristics from HEUR_ORDER."""
    known = [h for h in HEUR_ORDER if h in index]
    remaining = sorted([h for h in index if h not in HEUR_ORDER])
    return known + remaining


def extract_size_from_name(filename: str) -> str:
    """Extract the map size (e.g., '3x3', '5x5', etc.) from the filename."""
    name = os.path.basename(filename)
    for part in name.split("_"):
        if "x" in part:
            return part.replace(".csv", "").replace("N", "")
    return "unknown"


def compute_table_a_star(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter A* results and compute mean metrics grouped by heuristic.

    Args:
        df: Input DataFrame loaded from a results CSV file.

    Returns:
        A DataFrame containing the average metrics (d, g, #E, #F)
        for each heuristic used with A*.
    """
    a_star = df[df["algorithm"] == "astar"].copy()
    if a_star.empty:
        return pd.DataFrame(columns=METRICS)

    # Ensure metrics are numeric
    for m in METRICS:
        a_star[m] = pd.to_numeric(a_star[m], errors="coerce")

    grouped = (
        a_star.groupby("heuristic", dropna=False)[METRICS]
        .mean(numeric_only=True)
        .round(3)
    )

    if not grouped.empty:
        grouped = grouped.loc[order_heuristics(grouped.index)]
    return grouped


def main():
    os.makedirs(TABLES_DIR, exist_ok=True)
    files = sorted(glob.glob(PATTERN))

    if not files:
        print(f"No result files found matching pattern: {PATTERN}")
        return

    all_astar_rows = []

    for csv_path in files:
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"[WARN] Could not read {csv_path}: {e}")
            continue

        df.columns = [c.strip() for c in df.columns]
        required = {"map", "algorithm", "heuristic"} | set(METRICS)
        if not required.issubset(df.columns):
            print(f"[WARN] {csv_path} is missing required columns.")
            continue

        # Collect A* rows for the global table
        all_astar_rows.append(df[df["algorithm"] == "astar"].copy())

        # Compute table for this map size
        grouped = compute_table_a_star(df)
        size = extract_size_from_name(csv_path)
        out_path = os.path.join(TABLES_DIR, f"astar_table_{size}.csv")
        grouped.to_csv(out_path, index=True)
        print(f"Generated: {out_path}")

    # --- Global summary table (all map sizes combined) ---
    if all_astar_rows:
        big_df = pd.concat(all_astar_rows, ignore_index=True)
        general_table = compute_table_a_star(big_df)
        out_all = os.path.join(TABLES_DIR, "astar_table_all.csv")
        general_table.to_csv(out_all, index=True)
        print(f"Generated global summary: {out_all}")
    else:
        print("No A* rows found; global table was not generated.")

    print("\nDone.")


if __name__ == "__main__":
    main()
