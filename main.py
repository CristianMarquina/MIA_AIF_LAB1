import argparse
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

    args = parser.parse_args()

    map_path = args.map_path
    heuristic_choice = args.heuristic.lower()
    algorithm_choice = args.algorithm.lower()

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
    # 3. Run search algorithms
    # -------------------------------
    # Breadth-First Search (BFS)

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





    """breadth = breadth_first_graph_search(problem)
    print_path_trace(problem, breadth, "Breadth-First Search (BFS)", True)

    # Depth-First Search (DFS)
    depth = depth_first_graph_search(problem)
    print_path_trace(problem, depth, "Depth-First Search (DFS)", True)

    # A* Search
    if heuristic_choice == "default":
        astar = astar_search(problem)
    else:
        # You can extend this to support custom heuristics
        # Example: if the class has multiple heuristic methods
        if hasattr(problem, heuristic_choice):
            heuristic_func = getattr(problem, heuristic_choice)
            astar = astar_search(problem, h=heuristic_func)
        else:
            print(f"Warning: Heuristic '{heuristic_choice}' not found. Using default heuristic.")
            astar = astar_search(problem)

    print_path_trace(problem, astar, "A* Search", False)"""
