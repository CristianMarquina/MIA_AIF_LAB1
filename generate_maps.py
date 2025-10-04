#!/usr/bin/env python3
import argparse
import random
from pathlib import Path

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
        # 3) Initial position and orientation
        sx, sy, so = start
        f.write(f"{sx} {sy} {so}\n")
        # 4) Goal position and orientation
        gx, gy, go = goal
        f.write(f"{gx} {gy} {go}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Generate random map files for the DrillingRobot problem."
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
        help="Root output directory for the generated map files. Default: ./maps",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility (optional).",
    )
    args = parser.parse_args()

    # Apply random seed if provided
    if args.seed is not None:
        random.seed(args.seed)

    # Ensure base directory exists
    args.outdir.mkdir(parents=True, exist_ok=True)

    # --- Generate maps ---
    for n in args.sizes:
        subdir = args.outdir / f"N{n}x{n}"
        subdir.mkdir(parents=True, exist_ok=True)

        for i in range(1, args.per_size + 1):
            grid = generate_map(n, args.hardness_min, args.hardness_max)

            # Start fixed as (0, 0, North=0)
            start = (0, 0, 0)

            # Goal orientation (random 0–8 if not provided)
            goal_orientation = args.goal_orientation if args.goal_orientation is not None else random.randint(0, 8)
            goal = (n - 1, n - 1, goal_orientation)

            # Example: maps/N3x3/map1.txt
            filename = f"map{i}.txt"
            path = subdir / filename

            write_map_file(path, grid, start, goal)

            print(f"✓ Generated: {path} (goal orientation = {goal_orientation})")

if __name__ == "__main__":
    main()
