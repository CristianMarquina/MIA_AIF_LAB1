# Consts for DrillingRobot actions
TURN_RIGHT = "TURN_RIGHT"
TURN_LEFT = "TURN_LEFT"
DRILL = "DRILL"

# Mapping to show orientation in a readable format
ORIENTATION_NAMES = {
    0: 'North (0)', 1: 'Northeast (1)', 2: 'East (2)', 3: 'Southeast (3)',
    4: 'South (4)', 5: 'Southwest (5)', 6: 'West (6)', 7: 'Northwest (7)'
}

def print_path_trace(problem, solution_node, algorithm_name, is_blind_search):
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
            # We use the node cost as h(n) to avoid recalculation and assume that h is stored in the node
            h_val = node.h
            print(f"Node {i}: (depth:{node.depth}, total cost:{node.path_cost}, action:{operator}, h(n):{h_val}, State: x={x}, y={y}, o={orientation})")


    # 3. Print final metrics
    print("\n--- FINAL METRICS ---")
    print(f"Node {len(path) - 1} (final node)")
    print(f"Total path cost (g): {solution_node.path_cost}")
    print("-" * 60)

    
