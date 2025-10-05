#!/usr/bin/env python3
import argparse
import random
import re
from pathlib import Path
from typing import Optional

FILENAME_RE = re.compile(r"^map(\d+)\.txt$")

def generate_map(n: int, hmin: int, hmax: int) -> list[list[int]]:
    """Generate an n x n grid with integer hardness values in [hmin, hmax]."""
    return [[random.randint(hmin, hmax) for _ in range(n)] for _ in range(n)]

def write_map_file(path: Path, grid: list[list[int]], start: tuple[int,int,int], goal: tuple[int,int,int]) -> None:
    """Write the map file in the required format for the DrillingRobot problem."""
    n = len(grid)
    with path.open("w", encoding="utf-8") as f:
        # 1) Map dimensions
        f.write(f"{n} {n}\n")
        # 2) Terrain hardness grid
        for row in grid:
            f.write(" ".join(str(v) for v in row) + "\n")
        # 3) Initial position and orientation (x y o)
        sx, sy, so = start
        f.write(f"{sx} {sy} {so}\n")
        # 4) Goal position and orientation (x y o)
        gx, gy, go = goal
        f.write(f"{gx} {gy} {go}\n")

def find_next_id(subdir: Path) -> int:
    """
    Scan `subdir` for files named map{id}.txt, return max(id)+1.
    If none found, return 1.
    """
    max_id = 0
    if not subdir.exists():
        return 1
    for p in subdir.iterdir():
        if p.is_file():
            m = FILENAME_RE.match(p.name)
            if m:
                try:
                    idx = int(m.group(1))
                    if idx > max_id:
                        max_id = idx
                except ValueError:
                    # Ignore malformed names like mapXYZ.txt
                    pass
    return max_id + 1 if max_id >= 1 else 1

def main():
    parser = argparse.ArgumentParser(
        description="Generate random map files for the DrillingRobot problem, "
                    "continuing map IDs based on existing files."
    )
    parser.add_argument(
        "--sizes",
        type=int,
        nargs="+",
        default=[3, 5, 7, 9],
        help="Square map sizes N (generates N x N). Default: 3 5 7 9",
    )
    parser.add_argument(
        "--per-size",
        type=int,
        default=5,
        help="How many random maps to generate per size. Default: 5",
    )
    parser.add_argument(
        "--hardness-min",
        type=int,
        default=1,
        help="Minimum rock hardness value (inclusive). Default: 1",
    )
    parser.add_argument(
        "--hardness-max",
        type=int,
        default=9,
        help="Maximum rock hardness value (inclusive). Default: 9",
    )
    parser.add_argument(
        "--goal-orientation",
        type=int,
        choices=list(range(0, 9)),
        default=None,
        help="Goal orientation (0..7), or 8 for 'irrelevant'. "
             "If not specified, a random orientation between 0 and 8 will be chosen.",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("maps"),
        help="Root output directory. Subfolders N{N}x{N} will be created. Default: ./maps",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (optional).",
    )
    args = parser.parse_args()

    # Validations
    if args.hardness_min > args.hardness_max:
        parser.error("--hardness-min cannot be greater than --hardness-max")
    for n in args.sizes:
        if n <= 0:
            parser.error("All sizes must be positive integers")

    # Seed
    if args.seed is not None:
        random.seed(args.seed)

    # Ensure base dir
    args.outdir.mkdir(parents=True, exist_ok=True)

    # Generate per size
    for n in args.sizes:
        subdir = args.outdir / f"N{n}x{n}"
        subdir.mkdir(parents=True, exist_ok=True)

        # Determine starting id based on existing map{id}.txt files
        start_id = find_next_id(subdir)

        # Fixed start (0,0,North=0) per spec
        start_state = (0, 0, 0)

        # Generate maps
        for k in range(args.per_size):
            grid = generate_map(n, args.hardness_min, args.hardness_max)
            goal_orientation = args.goal_orientation if args.goal_orientation is not None else random.randint(0, 8)
            goal_state = (n - 1, n - 1, goal_orientation)

            file_id = start_id + k
            path = subdir / f"map{file_id}.txt"

            # Safety: never overwrite unexpectedly
            if path.exists():
                # Extremely unlikely if start_id was computed correctly, but safe-guard anyway
                # Skip to next available id
                while path.exists():
                    file_id += 1
                    path = subdir / f"map{file_id}.txt"

            write_map_file(path, grid, start_state, goal_state)
            print(f"Generated: {path}")

if __name__ == "__main__":
    main()
