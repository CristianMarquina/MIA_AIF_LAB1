#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Genera tablas CSV con las medias (d, g, #E, #F) por heurística usando A*.

Lee ficheros en results/ como:
  results/results_N3x3.csv, results/results_5x5.csv, results/results_7x7.csv, results/results_9x9.csv

Genera:
  tables/astar_table_3x3.csv
  tables/astar_table_5x5.csv
  tables/astar_table_7x7.csv
  tables/astar_table_9x9.csv
  tables/astar_table_all.csv   <- tabla general (todas las dimensiones juntas)
"""

import os
import glob
import pandas as pd

RESULTS_DIR = "results"
TABLES_DIR = "tables"
PATTERN = os.path.join(RESULTS_DIR, "results_*x*.csv")

METRICS = ["d", "g", "#E", "#F"]

# Orden preferido de heurísticas
HEUR_ORDER = ["h", "h_chebyshev", "h_euclidean", "h_minhardness", "h_combined"]

def order_heuristics(index):
    known = [h for h in HEUR_ORDER if h in index]
    rest = sorted([h for h in index if h not in HEUR_ORDER])
    return known + rest

def extract_size_from_name(filename: str) -> str:
    """Extrae '3x3', '5x5', etc. del nombre del archivo."""
    name = os.path.basename(filename)
    for part in name.split("_"):
        if "x" in part:
            return part.replace(".csv", "").replace("N", "")
    return "unknown"

def compute_table_a_star(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra A* y devuelve medias por heurística en METRICS."""
    a_star = df[df["algorithm"] == "astar"].copy()
    if a_star.empty:
        return pd.DataFrame(columns=METRICS)

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
        print(f"No se encontraron archivos con el patrón: {PATTERN}")
        return

    # Para la tabla general
    all_astar_rows = []

    for csv_path in files:
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"[WARN] No se pudo leer {csv_path}: {e}")
            continue

        df.columns = [c.strip() for c in df.columns]
        needed = {"map", "algorithm", "heuristic"} | set(METRICS)
        if not needed.issubset(df.columns):
            print(f"[WARN] {csv_path} no tiene las columnas necesarias.")
            continue

        # Acumular para la tabla general
        all_astar_rows.append(df[df["algorithm"] == "astar"].copy())

        # Tabla por tamaño
        grouped = compute_table_a_star(df)
        size = extract_size_from_name(csv_path)
        out_path = os.path.join(TABLES_DIR, f"astar_table_{size}.csv")
        grouped.to_csv(out_path, index=True)
        print(f"✅ Generado: {out_path}")

    # --- Tabla general (todas las dimensiones juntas) ---
    if all_astar_rows:
        big_df = pd.concat(all_astar_rows, ignore_index=True)
        general_table = compute_table_a_star(big_df)
        out_all = os.path.join(TABLES_DIR, "astar_table_all.csv")
        general_table.to_csv(out_all, index=True)
        print(f"✅ Generado (general): {out_all}")
    else:
        print("[INFO] No se generó tabla general: no hay filas de A*.")

    print("\nListo.")

if __name__ == "__main__":
    main()
