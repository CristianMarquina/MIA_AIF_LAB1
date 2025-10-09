#!/bin/bash
# ============================================================
# run_all_experiments.sh
# 1) Generate random maps (seed=123)
# 2) For each subfolder in maps/, run bfs, dfs, and astar
#    For astar, run multiple heuristics
# 3) Save one CSV per subfolder inside results/
# 4) Generate summary tables (A* heuristics + algorithm comparison)
# ============================================================

set -e

MAIN_SCRIPT="main.py"
GEN_SCRIPT="generate_maps.py"
MAPS_DIR="maps"
RESULTS_DIR="results"

# Table-generation scripts
ASTAR_TABLES_SCRIPT="generate_astar_tables.py"
ALG_TABLES_SCRIPT="generate_alg_tables.py"
ALG_HEUR="h_combined"

# Algorithms and heuristics to test
ALGORITHMS=("bfs" "dfs" "astar")
ASTAR_HEURISTICS=("h" "h_chebyshev" "h_euclidean" "h_minhardness" "h_combined")

# --- Step 1: Generate maps ---------------------------------------------------
echo "Generating maps with fixed seed 123..."
if [ ! -f "$GEN_SCRIPT" ]; then
  echo "ERROR: $GEN_SCRIPT not found."
  exit 1
fi
python3 "$GEN_SCRIPT" --seed 123
echo "Maps generated in '$MAPS_DIR/'"
echo

# --- Step 2: Check dependencies ---------------------------------------------
if [ ! -f "$MAIN_SCRIPT" ]; then
  echo "ERROR: $MAIN_SCRIPT not found."
  exit 1
fi
if [ ! -d "$MAPS_DIR" ]; then
  echo "ERROR: Directory '$MAPS_DIR' not found."
  exit 1
fi

# --- Step 3: Ensure results directory exists --------------------------------
mkdir -p "$RESULTS_DIR"

# --- Step 4: Iterate over map subfolders ------------------------------------
for SUBDIR in "$MAPS_DIR"/*; do
  if [ -d "$SUBDIR" ]; then
    SIZE_NAME=$(basename "$SUBDIR")
    CSV_FILE="$RESULTS_DIR/results_${SIZE_NAME}.csv"

    echo "=============================================="
    echo "Processing folder: $SUBDIR"
    echo "Output CSV: $CSV_FILE"
    echo "=============================================="

    # Remove old CSV if it exists
    if [ -f "$CSV_FILE" ]; then
      echo "Removing old CSV: $CSV_FILE"
      rm "$CSV_FILE"
    fi

    shopt -s nullglob
    MAP_FILES=("$SUBDIR"/map*.txt)
    shopt -u nullglob

    if [ ${#MAP_FILES[@]} -eq 0 ]; then
      echo "No map*.txt files in $SUBDIR, skipping."
      echo
      continue
    fi

    # Run all algorithms on each map
    for MAP_FILE in "${MAP_FILES[@]}"; do
      echo "Map: $MAP_FILE"

      for ALG in "${ALGORITHMS[@]}"; do
        if [ "$ALG" != "astar" ]; then
          echo "  Running $ALG ..."
          python3 "$MAIN_SCRIPT" "$MAP_FILE" -a "$ALG" -o "$CSV_FILE"
        else
          for H in "${ASTAR_HEURISTICS[@]}"; do
            echo "  Running astar with heuristic: $H ..."
            python3 "$MAIN_SCRIPT" "$MAP_FILE" -a astar --heuristic "$H" -o "$CSV_FILE"
          done
        fi
      done
    done

    echo "Finished processing: $CSV_FILE"
    echo
  fi
done

# --- Step 5: Generate summary tables ----------------------------------------
echo "Generating A* heuristic tables..."
if [ ! -f "$ASTAR_TABLES_SCRIPT" ]; then
  echo "ERROR: $ASTAR_TABLES_SCRIPT not found."
  exit 1
fi
python3 "$ASTAR_TABLES_SCRIPT"

echo "Generating algorithm-comparison tables (A* heuristic = $ALG_HEUR)..."
if [ ! -f "$ALG_TABLES_SCRIPT" ]; then
  echo "ERROR: $ALG_TABLES_SCRIPT not found."
  exit 1
fi
python3 "$ALG_TABLES_SCRIPT" -H "$ALG_HEUR"

echo "All experiments and table generations completed successfully."
