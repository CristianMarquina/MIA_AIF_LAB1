#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Genera tablas CSV comparando algoritmos (bfs, dfs, astar) para una heurística seleccionada.

Entrada (CSV en ./results):
  results/results_N3x3.csv, results/results_5x5.csv, results/results_7x7.csv, results/results_9x9.csv

Uso:
  python make_algo_tables.py --heur h_euclidean
  # o
  python make_algo_tables.py -H h

Salida (en ./tables):
  tables/algo_table_3x3_h.csv
  tables/algo_table_5x5_h.csv
  tables/algo_table_7x7_h.csv
  tables/algo_table_9x9_h.csv
  tables/algo_table_all_h.csv

Cada tabla: filas = algoritmos (bfs, dfs, astar), columnas = d,g,#E,#F
 - Para astar, solo filas con heuristic == <heurística elegida>
 - Para bfs/dfs, se incluyen independientemente de la columna heuristic (suele ser 'N/A')
"""

import os
import glob
import argparse
import pandas as pd

RESULTS_DIR = "results"
TABLES_DIR = "tables"
PATTERN = os.path.join(RESULTS_DIR, "results_*x*.csv")

METRICS = ["d", "g", "#E", "#F"]
ALG_ORDER = ["bfs", "dfs", "astar"]  # orden deseado en la tabla

def extract_size_from_name(filename: str) -> str:
    """Extrae '3x3', '5x5', etc. del nombre del archivo."""
    name = os.path.basename(filename)
    for part in name.split("_"):
        if "x" in part:
            return part.replace(".csv", "").replace("N", "")
    return "unknown"

def compute_table_for_size(df: pd.DataFrame, chosen_heur: str) -> pd.DataFrame:
    """
    Devuelve un DataFrame con medias por algoritmo (bfs, dfs, astar con chosen_heur).
    Columnas: METRICS | Índice: algorithm
    """
    # Normaliza nombres de columnas
    df.columns = [c.strip() for c in df.columns]

    # Validación mínima
    needed = {"map", "algorithm", "heuristic"} | set(METRICS)
    if not needed.issubset(df.columns):
        # Devuelve tabla vacía con estructura esperada
        return pd.DataFrame(columns=METRICS, index=ALG_ORDER)

    # Asegurar tipos numéricos
    df_num = df.copy()
    for m in METRICS:
        df_num[m] = pd.to_numeric(df_num[m], errors="coerce")

    # Filtrado por algoritmo:
    bfs_rows = df_num[df_num["algorithm"] == "bfs"]
    dfs_rows = df_num[df_num["algorithm"] == "dfs"]
    astar_rows = df_num[(df_num["algorithm"] == "astar") & (df_num["heuristic"] == chosen_heur)]

    # Agrupa y promedia
    parts = []
    if not bfs_rows.empty:
        g_bfs = bfs_rows.groupby("algorithm")[METRICS].mean(numeric_only=True)
        parts.append(g_bfs)
    if not dfs_rows.empty:
        g_dfs = dfs_rows.groupby("algorithm")[METRICS].mean(numeric_only=True)
        parts.append(g_dfs)
    if not astar_rows.empty:
        g_astar = astar_rows.groupby("algorithm")[METRICS].mean(numeric_only=True)
        parts.append(g_astar)

    if parts:
        table = pd.concat(parts, axis=0)
    else:
        table = pd.DataFrame(columns=METRICS)

    # Reordenar filas según ALG_ORDER; si falta alguna, no revienta
    if not table.empty:
        # Eliminar duplicados por si acaso y asegurar el orden
        table = table[~table.index.duplicated(keep="first")]
        ordered_index = [a for a in ALG_ORDER if a in table.index]
        # Añadir también cualquier otro algoritmo desconocido (por si existe) ordenado alfabéticamente
        rest = sorted([a for a in table.index if a not in ALG_ORDER])
        table = table.loc[ordered_index + rest]
        table = table.round(3)

    return table

def main():
    parser = argparse.ArgumentParser(description="Genera tablas comparando algoritmos para una heurística concreta.")
    parser.add_argument("-H", "--heur", required=True, help="Nombre de la heurística a usar para A* (ej.: h, h_euclidean, h_chebyshev, h_minhardness, h_combined)")
    args = parser.parse_args()
    chosen_heur = args.heur

    os.makedirs(TABLES_DIR, exist_ok=True)
    files = sorted(glob.glob(PATTERN))

    if not files:
        print(f"No se encontraron archivos con el patrón: {PATTERN}")
        return

    # Para la tabla general
    all_dfs = []

    for csv_path in files:
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"[WARN] No se pudo leer {csv_path}: {e}")
            continue

        size = extract_size_from_name(csv_path)
        table = compute_table_for_size(df, chosen_heur)
        out_path = os.path.join(TABLES_DIR, f"alg_table_{size}.csv")
        table.to_csv(out_path, index=True)
        print(f"✅ Generado: {out_path}")

        # Acumular para tabla general
        all_dfs.append(df)

    # --- Tabla general (todas las dimensiones) ---
    if all_dfs:
        big_df = pd.concat(all_dfs, ignore_index=True)
        general_table = compute_table_for_size(big_df, chosen_heur)
        out_all = os.path.join(TABLES_DIR, f"alg_table_all.csv")
        general_table.to_csv(out_all, index=True)
        print(f"✅ Generado (general): {out_all}")
    else:
        print("[INFO] No se generó tabla general: no se leyeron CSV.")

    print("\nListo.")

if __name__ == "__main__":
    main()
