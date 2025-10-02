from DrillingRobot import DrillingRobot
from search import breadth_first_graph_search, depth_first_graph_search, astar_search, Node


# Mapping to show orientation in a readable format
ORIENTATION_NAMES = {
    0: 'North (0)', 1: 'Northeast (1)', 2: 'East (2)', 3: 'Southeast (3)',
    4: 'South (4)', 5: 'Southwest (5)', 6: 'West (6)', 7: 'Northwest (7)'
}


def print_path_trace(solution_node, algorithm_name, is_blind_search):
    """
    Prints the execution trace of the found solution,
    following the format requested in Section 4.2 of the statement.
    """
    print("=" * 60)
    print(f"ALGORITHM: {algorithm_name}")
    print("=" * 60)

    if not solution_node:
        print("WARNING! No solution found. Showing trace up to the last examined node.")
        print("End of execution without solution.")
        return

    # 1. Rebuild the path from the final node back to the root (initial node)
    path = solution_node.path()

    # 2. Print the execution trace
    print("--- EXECUTION TRACE (SOLUTION) ---")
    
    # The first node is the root node (no previous operator)
    root_node = path[0]
    x, y, o = root_node.state
    orientation = ORIENTATION_NAMES.get(o, 'N/A')
    
    # Node 0: (d, g(n), op, S) or (d, g(n), op, h(n), S)
    if is_blind_search:
        print(f"Node 0 (starting node): (depth:{root_node.depth}, total cost:{root_node.path_cost}, action:None, State: x={x}, y={y}, o={orientation})")
    else: # A*
        h_val = problem.h(root_node) # Calculate h(n) for the root
        print(f"Node 0 (starting node): (depth:{root_node.depth}, total cost:{root_node.path_cost}, action:None, h(n):{h_val}, State: x={x}, y={y}, o={orientation})")


    # Print the remaining nodes (from 1 to N)
    for i in range(1, len(path)):
        node = path[i]
        operator = path[i].action

        x, y, o = node.state
        orientation = ORIENTATION_NAMES.get(o, 'N/A')

        # Print Node i
        if is_blind_search:
            print(f"Node {i}: (depth:{node.depth}, total cost:{node.path_cost}, action:{operator}, State: x={x}, y={y}, o={orientation})")
        else: # A*
            # Usamos el costo del nodo como h(n) para no re-calcular y asumir que h está almacenado en el nodo
            h_val = node.h
            print(f"Node {i}: (depth:{node.depth}, total cost:{node.path_cost}, action:{operator}, h(n):{h_val}, State: x={x}, y={y}, o={orientation})")


    # 3. Print final metrics
    print("\n--- FINAL METRICS ---")
    print(f"Node {len(path) - 1} (final node)")
    print(f"Total path cost (g): {solution_node.path_cost}")
    print("-" * 60)


if __name__ == '__main__':

    # 1. Define the map path 
    mapa = "mapa.txt" 
    
    # 2. Create an instance of the problem
    try:
        problem = DrillingRobot(mapa)
    except FileNotFoundError:
        print(f"ERROR: Map file '{mapa}' not found. Please check the path.")
        exit()
    except Exception as e:
        print(f"An error occurred while loading the map: {e}")
        exit()
        
    print(f"Problem loaded: From {problem.initial} to {problem.goal}")


    # 3. Execute the three required algorithms
    # Breadth-First Search (BFS)
    breadth = breadth_first_graph_search(problem)
    print_path_trace(breadth, "Breadth-First Search (BFS)", True)

    # Depth-First Search (DFS)
    depth = depth_first_graph_search(problem)
    print_path_trace(depth, "Depth-First Search (DFS)", True)

    # 3.3. A* Search
    astar = astar_search(problem)
    print_path_trace(astar, "A* Search", False)

    
