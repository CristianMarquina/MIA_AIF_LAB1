# MIA_AIF_LAB1

This repository is for solving the problem from Lab 1 of the AIF course.

## Project Description

This project consists of the implementation and comparison of Artificial Intelligence search algorithms to solve a pathfinding problem. The objective is to find the minimum-cost path for a drilling robot from a starting point to a target location on a terrain with varying levels of hardness, respecting the robot's movement and orientation constraints.

The following algorithms are implemented and compared:

* **Blind Search**:

    * Breadth-First Search (BFS)
    * Depth-First Search (DFS)

* **Informed Search**:

    * A* (A-Star)

---

## Getting Started

Follow these steps to set up and run the project on your local machine.

### Installation

1.  **Clone the repository** to your local machine:
    ```bash
    git clone https://github.com/CristianMarquina/MIA_AIF_LAB1.git
    cd MIA_AIF_LAB1
    ```
2.  **Install dependencies**. This command reads the `requirements.txt` file and installs all the necessary libraries for the project to run.
    ```bash
    pip install -r requirements.txt
    ```
---

## Usage Guide

The main entry point of the project is the `main.py` script, which runs a selected search algorithm (BFS, DFS, or A*) on a specific map file.  
It can be executed directly from the command line, allowing you to define the map path, the algorithm, and optionally, the heuristic and an output file for saving results.

### Command Structure

The general syntax is:
```bash
python main.py <map_path> -a <algorithm>
```

### Available Algorithms

1. Breadth-First Search (BFS)
   ```bash
   python main.py <map_path> -a bfs
   ```
2. Depth-First Search (DFS)
   ```bash
   python main.py <map_path> -a dfs
   ```
3. A* Search (A*)
   ```bash
   python main.py <map_path> -a astar
   ```

### A* Heuristics

When using A*, the default heuristic is the **Manhattan distance**, but several other heuristics are implemented and can be specified using the `--heuristic` argument:

| Heuristic name | Description |
|-----------------|--------------|
| `h` | Manhattan distance |
| `h_chebyshev` | Chebyshev distance (8-directional movement) |
| `h_euclidean` | Euclidean distance (straight-line distance) |
| `h_minhardness` | Chebyshev distance scaled by the minimum rock hardness |
| `h_combined` | Combined heuristic: (Chebyshev × min_hardness) + orientation adjustment |

Example:
```bash
python main.py <map_path> -a astar --heuristic h_combined
```

### Optional Output

You can also include an optional output path using the `-o` or `--output` argument to automatically append the results to a CSV file:
```bash
python main.py <map_path> -a astar --heuristic h_combined -o results/results_example.csv
```
This will record the performance metrics (`d`, `g`, `#E`, `#F`) for the selected algorithm and heuristic in the specified file.

---

## Running the Complete Experimentation Pipeline

Although `main.py` can be used for individual tests, the repository includes a full automation script called **`run_experiments.sh`**, which reproduces the entire set of experiments described in the report.

### What the Script Does

1. **Generates random maps** of different sizes (3×3, 5×5, 7×7, 9×9) with a fixed seed for reproducibility, using the script `generate_maps.py`.
2. **Runs all algorithms** (`bfs`, `dfs`, and `astar`) on every map file inside the `maps/` directory.  
   - For A*, it executes each heuristic: `h`, `h_chebyshev`, `h_euclidean`, `h_minhardness`, and `h_combined`.
3. **Saves the results** of all runs in corresponding CSV files under the `results/` directory (one per map size).
4. **Generates summary tables** automatically:
   - `generate_astar_tables.py`: computes performance statistics for all A* heuristics.
   - `generate_alg_tables.py`: compares all algorithms (BFS, DFS, and A*) using the `h_combined` heuristic (the most suitable for this case).
5. The tables are stored in the `tables/` directory.

To execute the full experimental process:
```bash
./run_experiments.sh
```
This script will automatically generate maps, execute all experiments, and create all result tables. No manual intervention is required.

## Visualize Tree Search

In addition to the main experimentation pipeline, an optional visualization script is provided to **generate graphical representations of the search tree** for any specific map and algorithm.

The script is called **`visualize_tree.py`**, and it allows you to execute a search (BFS, DFS, or A*) on a chosen map file and automatically produce a `.png` image of the resulting search tree.

### Requirements

This visualization tool requires the **Graphviz** library to be installed on your system.  
> ⚠️ **Important:** Graphviz is **not included in `requirements.txt`**, because it cannot always be installed reliably via `pip`.  
> You must install it manually on your operating system before running this script.

Typical installation commands:
```bash
sudo apt install graphviz        # Ubuntu / Debian
brew install graphviz            # macOS (Homebrew)
choco install graphviz           # Windows (Chocolatey)
```

Once Graphviz is installed on your system, you can install the Python bindings if needed:
```bash
pip install graphviz
```

### Usage

You can generate a search tree visualization for a specific map and algorithm as follows:

```bash
python visualize_tree.py <map_path> -a <algorithm> [--heuristic <heuristic>] [-o <output_name>]
```

This will produce an image file showing the search tree structure, where:

- 🟩 **Green nodes** represent the solution path.  
- 🟥 **Red nodes** represent expanded states.  
- 🟦 **Blue nodes** represent generated (but not expanded) states.

