import argparse
import csv
from pathlib import Path
from DrillingRobot import DrillingRobot
from drilling_utils import *
from search import breadth_first_graph_search, depth_first_graph_search, astar_search


if __name__ == '__main__':
    # -------------------------------
    # 1. Parse command-line arguments
    # -------------------------------
    parser = argparse.ArgumentParser(
        description="Run search algorithms on the DrillingRobot problem."
    )
    parser.add_argument(
        "map_path",
        type=str,
        help="Path to the input map file (required)."
    )
    parser.add_argument(
        "--heuristic",
        type=str,
        default="default",
        help="Heuristic function to use with A* (optional)."
    )
    parser.add_argument(
        "-a", "--algorithm",
        type=str,
        required=True,
        choices=['bfs', 'dfs', 'astar'],
        help="The search algorithm to run (bfs, dfs, or astar)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Optional path to a CSV file where the results will be saved."
    )

    args = parser.parse_args()

    map_path = args.map_path
    heuristic_choice = args.heuristic.lower()
    algorithm_choice = args.algorithm.lower()
    output_path = args.output

    # -------------------------------
    # 2. Create problem instance
    # -------------------------------
    try:
        problem = DrillingRobot(map_path)
    except FileNotFoundError:
        print(f"ERROR: Map file '{map_path}' not found. Please check the path.")
        exit(1)
    except Exception as e:
        print(f"An error occurred while loading the map: {e}")
        exit(1)

    print(f"Problem loaded: From {problem.initial} to {problem.goal}")
    print(f"Heuristic selected: {heuristic_choice}")

    # -------------------------------
    # 3. Run the selected algorithm
    # -------------------------------
    solution_node = None
    algorithm_name = ""
    is_blind = False

    if algorithm_choice == 'bfs':
        solution_node = breadth_first_graph_search(problem)
        algorithm_name = "Breadth-First Search (BFS)"
        is_blind = True

    elif algorithm_choice == 'dfs':
        solution_node = depth_first_graph_search(problem)
        algorithm_name = "Depth-First Search (DFS)"
        is_blind = True

    elif algorithm_choice == 'astar':
        if heuristic_choice == "default":
            solution_node = astar_search(problem)
        elif hasattr(problem, heuristic_choice):
            heuristic_func = getattr(problem, heuristic_choice)
            solution_node = astar_search(problem, h=heuristic_func)
        else:
            print(f"Warning: Heuristic '{heuristic_choice}' not found. Using default.")
            solution_node = astar_search(problem)
        
        algorithm_name = f"A* Search (heuristic: {heuristic_choice})"
        is_blind = False
    
    print_path_trace(problem, solution_node, algorithm_name, is_blind)

    # -------------------------------
    # 4. Collect performance metrics
    # -------------------------------
    d = getattr(solution_node, "depth", None)
    g = getattr(solution_node, "path_cost", None)
    explored = getattr(problem, "expanded_nodes", None)
    frontier = getattr(problem, "final_frontier", None)

    print("\n--- Search Statistics ---")
    print(f"d (solution depth): {d}")
    print(f"g (solution cost): {g}")
    print(f"#E (expanded nodes): {explored}")
    print(f"#F (final frontier size): {frontier}")

    # -------------------------------
    # 5. Save results to CSV (optional)
    # -------------------------------
    if output_path:
        try:
            output_file = Path(output_path)
            write_header = not output_file.exists()

            row = {
                'map': map_path,
                'algorithm': algorithm_choice,
                'heuristic': heuristic_choice if algorithm_choice == 'astar' else 'N/A',
                'd': d,
                'g': g,
                '#E': explored,
                '#F': frontier,
            }

            with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=row.keys())
                if write_header:
                    writer.writeheader()
                writer.writerow(row)

            print(f"\nResults saved to {output_path}")
        except Exception as e:
            print(f"Could not save results to CSV: {e}")