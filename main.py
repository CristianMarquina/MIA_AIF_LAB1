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
    # Visualization of the tree
    parser.add_argument(
        "--draw-tree",
        default=False,
        action="store_true",
        help="If set, visualizes the search tree after the algorithm finishes."
    )

    args = parser.parse_args()

    map_path = args.map_path
    heuristic_choice = args.heuristic.lower()
    algorithm_choice = args.algorithm.lower()
    output_path = args.output
    draw_tree = args.draw_tree

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

    # -------------------------------
    # 3. Run the selected algorithm
    # -------------------------------
    solution_node = None
    algorithm_name = ""
    is_blind = False

    if algorithm_choice == 'bfs':
        solution_node, gen, exp, edges, order, frontier = breadth_first_graph_search(problem)
        algorithm_name = "Breadth-First Search (BFS)"
        is_blind = True

    elif algorithm_choice == 'dfs':
        solution_node, gen, exp, edges, order, frontier = depth_first_graph_search(problem)
        algorithm_name = "Depth-First Search (DFS)"
        is_blind = True

    elif algorithm_choice == 'astar':
        if heuristic_choice == "default":
            solution_node, gen, exp, edges, order, frontier = astar_search(problem)
        elif hasattr(problem, heuristic_choice):
            heuristic_func = getattr(problem, heuristic_choice)
            solution_node, gen, exp, edges, order, frontier = astar_search(problem, h=heuristic_func)
        else:
            print(f"Warning: Heuristic '{heuristic_choice}' not found. Using default.")
            solution_node, gen, exp, edges, order, frontier = astar_search(problem)
        
        algorithm_name = f"A* Search (heuristic: {heuristic_choice})"
        is_blind = False

    # -------------------------------
    # 4. Print performance metrics
    # -------------------------------
    print_path_trace(problem, solution_node, algorithm_name, is_blind)
    
    d = getattr(solution_node, "depth", None)
    g = getattr(solution_node, "path_cost", None)
    explored = len(exp)
    f = len(frontier)

    print(f"\nTotal number of items in explored list: {explored}")
    print(f"Total number of items in frontier: {f}")

    # -------------------------------
    # 5. Visualize Search Tree (optional)
    # -------------------------------
    if draw_tree:
        if solution_node and gen and exp and edges and order:
            # Genera un nombre de archivo dinámico
            filename = algorithm_choice
            if algorithm_choice == 'astar':
                filename += f"_{heuristic_choice}"
            filename += "_tree"
            
            print(f"\n--- Visualizing Search Tree ---")
            print(f"Drawing tree to {filename}.png...")

            try:
                # Llama a la función con los 5 argumentos del árbol + solution_node
                draw_search_tree(gen, exp, edges, order, filename, solution_node=solution_node)
            except NameError:
                print("ERROR: The 'draw_search_tree' function is not available or was not imported correctly.")
            except Exception as e:
                print(f"An error occurred while drawing the tree: {e}")
        else:
            print("\nVisualization skipped: Missing solution node or tree generation data (gen, exp, edges, order).")


    # -------------------------------
    # 6. Save results to CSV (optional)
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
                '#F': f,
            }

            with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=row.keys())
                if write_header:
                    writer.writeheader()
                writer.writerow(row)

            print(f"\nResults saved to {output_path}")
        except Exception as e:
            print(f"Could not save results to CSV: {e}")