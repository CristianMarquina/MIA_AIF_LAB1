#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generates CSV summary tables comparing algorithms (BFS, DFS, A*).

Input (CSV files in ./results):
  results/results_N3x3.csv, results/results_5x5.csv, results/results_7x7.csv, results/results_9x9.csv

Usage:
  python generate_alg_tables.py --heur h_euclidean
  # or
  python generate_alg_tables.py -H h

Output (in ./tables):
  tables/alg_table_3x3.csv
  tables/alg_table_5x5.csv
  tables/alg_table_7x7.csv
  tables/alg_table_9x9.csv
  tables/alg_table_all.csv

Each table: rows = algorithms (bfs, dfs, astar), columns = d, g, #E, #F
 - For A*, only rows matching the chosen heuristic are included.
 - For BFS and DFS, all rows are included regardless of heuristic.
"""

import os
import glob
import argparse
import pandas as pd

RESULTS_DIR = "results"
TABLES_DIR = "tables"
PATTERN = os.path.join(RESULTS_DIR, "results_*x*.csv")

METRICS = ["d", "g", "#E", "#F"]
ALG_ORDER = ["bfs", "dfs", "astar"]  # Desired output order


def extract_size_from_name(filename: str) -> str:
    """Extracts the grid size (e.g., '3x3', '5x5', etc.) from the filename."""
    name = os.path.basename(filename)
    for part in name.split("_"):
        if "x" in part:
            return part.replace(".csv", "").replace("N", "")
    return "unknown"


def compute_table_for_size(df: pd.DataFrame, chosen_heur: str) -> pd.DataFrame:
    """
    Compute mean metrics per algorithm (bfs, dfs, astar with chosen heuristic).

    Args:
        df: Input DataFrame loaded from results CSV.
        chosen_heur: Heuristic name to filter A* runs.

    Returns:
        A DataFrame with average values for each algorithm:
        columns = METRICS, index = algorithm.
    """
    df.columns = [c.strip() for c in df.columns]

    required = {"map", "algorithm", "heuristic"} | set(METRICS)
    if not required.issubset(df.columns):
        # Return empty placeholder if columns are missing
        return pd.DataFrame(columns=METRICS, index=ALG_ORDER)

    # Convert metrics to numeric values (ignore errors)
    df_num = df.copy()
    for m in METRICS:
        df_num[m] = pd.to_numeric(df_num[m], errors="coerce")

    # Filter per algorithm
    bfs_rows = df_num[df_num["algorithm"] == "bfs"]
    dfs_rows = df_num[df_num["algorithm"] == "dfs"]
    astar_rows = df_num[
        (df_num["algorithm"] == "astar") & (df_num["heuristic"] == chosen_heur)
    ]

    # Group and compute mean metrics
    parts = []
    if not bfs_rows.empty:
        parts.append(bfs_rows.groupby("algorithm")[METRICS].mean(numeric_only=True))
    if not dfs_rows.empty:
        parts.append(dfs_rows.groupby("algorithm")[METRICS].mean(numeric_only=True))
    if not astar_rows.empty:
        parts.append(astar_rows.groupby("algorithm")[METRICS].mean(numeric_only=True))

    if parts:
        table = pd.concat(parts, axis=0)
    else:
        table = pd.DataFrame(columns=METRICS)

    # Order rows by ALG_ORDER; ignore missing ones
    if not table.empty:
        table = table[~table.index.duplicated(keep="first")]
        ordered = [a for a in ALG_ORDER if a in table.index]
        remaining = sorted([a for a in table.index if a not in ALG_ORDER])
        table = table.loc[ordered + remaining]
        table = table.round(3)

    return table


def main():
    parser = argparse.ArgumentParser(
        description="Generate comparison tables for different algorithms given a specific heuristic."
    )
    parser.add_argument(
        "-H",
        "--heur",
        required=True,
        help="Heuristic name to use for A* (e.g., h, h_euclidean, h_chebyshev, h_minhardness, h_combined).",
    )
    args = parser.parse_args()
    chosen_heur = args.heur

    os.makedirs(TABLES_DIR, exist_ok=True)
    files = sorted(glob.glob(PATTERN))

    if not files:
        print(f"No result files found matching pattern: {PATTERN}")
        return

    all_dfs = []

    for csv_path in files:
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"[WARN] Could not read {csv_path}: {e}")
            continue

        size = extract_size_from_name(csv_path)
        table = compute_table_for_size(df, chosen_heur)

        out_path = os.path.join(TABLES_DIR, f"alg_table_{size}.csv")
        table.to_csv(out_path, index=True)
        print(f"Generated: {out_path}")

        all_dfs.append(df)

    # Global summary table (across all map sizes)
    if all_dfs:
        big_df = pd.concat(all_dfs, ignore_index=True)
        general_table = compute_table_for_size(big_df, chosen_heur)

        out_all = os.path.join(TABLES_DIR, "alg_table_all.csv")
        general_table.to_csv(out_all, index=True)
        print(f"Generated global summary: {out_all}")
    else:
        print("No CSV files were successfully read; global table not generated.")

    print("\nDone.")


if __name__ == "__main__":
    main()
