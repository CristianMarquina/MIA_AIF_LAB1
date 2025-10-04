from DrillingRobot import DrillingRobot
from search import breadth_first_graph_search, depth_first_graph_search, astar_search, astar_search_with_log, Node
from graphviz import Digraph
from collections import defaultdict


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
            # Use the node cost as h(n) to avoid recalculation and assume that h is stored in the node
            h_val = node.h
            print(f"Node {i}: (depth:{node.depth}, total cost:{node.path_cost}, action:{operator}, h(n):{h_val}, State: x={x}, y={y}, o={orientation})")


    # 3. Print final metrics
    print("\n--- FINAL METRICS ---")
    print(f"Node {len(path) - 1} (final node)")
    print(f"Total path cost (g): {solution_node.path_cost}")
    print("-" * 60)





def draw_search_tree(gen, exp, edges, node_list_in_order, filename, solution_node=None):
    
    # 0. Crear un mapa Estado -> Objeto Node para obtener la información de forma robusta
    state_to_node_map = {node.state: node for node in gen}
    
    # --- CONFIGURATION ---
    dot = Digraph(comment='Search Tree', 
                   graph_attr={
                       'rankdir': 'TB',          # Top to Bottom
                       'splines': 'polyline',    # Líneas rectas (menos cruces)
                       'overlap': 'false',       # Evita que los nodos se superpongan
                       'dpi': '150',
                       'ranksep': '1.5',         # Gran separación vertical (CRÍTICO para A*)
                       'nodesep': '0.7',         # Separación horizontal
                       'concentrate': 'false'    # No concentrar aristas
                   }, 
                   node_attr={'shape': 'box', 'width': '2.2', 'height': '0.9', 'fixedsize': 'true', 'style': 'filled'}, 
                   edge_attr={
                       'fontsize': '13',          
                       'labelfloat': 'true',
                       'labeldistance': '2.5',   
                       'labelangle': '-20'
                   })
    
    ordered_depth_groups = defaultdict(list)
    
    # --- COLOR LOGIC ---
    solution_path_states = set()
    if solution_node:
        # States in the solution path
        solution_path_states = {n.state for n in solution_node.path()} 
        
    # Expanded states
    expanded_states = {n.state for n in exp}

    # 1. Compute all the nodes
    for item in node_list_in_order:
        node_state = item.state if hasattr(item, 'state') else item
        
        if node_state not in state_to_node_map:
             continue 
        
        node = state_to_node_map[node_state]
        node_key = str(node_state)
        
        # Color definition
        color = 'lightblue' # Generated, not expanded
        if node_state in expanded_states:
            color = 'lightcoral' # Expanded
        if node_state in solution_path_states:
            color = 'lightgreen' # Solution
            
        # Generation of the lable for each node
        label = (f'#{node.expansion_order}\n'
                 f'S: {node.state}\n'
                 f'd: {node.depth}\n'
                 f'g(n): {node.path_cost:.1f}')
    
        
        dot.node(node_key, label=label, style='filled', fillcolor=color)
        
        ordered_depth_groups[node.depth].append(node_key)

    # 2. Draw the edges
    for parent, child in edges:
        dot.edge(str(parent.state), str(child.state), label=str(child.action))

    dot.render(filename, format="png", cleanup=True)
    print(f"Árbol guardado en {filename}.png")





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
    ## Breadth-First Search (BFS)
    ##TODO: CHECK if we need to have the 4 comments below
    breadth, gen, exp, edges, order = breadth_first_graph_search(problem)
    print_path_trace(breadth, "Breadth-First Search (BFS)", True)
    draw_search_tree(gen, exp, edges, order, "bfs_tree", solution_node=breadth) # <-- Pass the solution node

    # Depth-First Search (DFS)
    depth, gen, exp, edges, order = depth_first_graph_search(problem)
    print_path_trace(depth, "Depth-First Search (DFS)", True)
    draw_search_tree(gen, exp, edges, order, "dfs_tree", solution_node=depth) # <-- Pass the solution node

    # A* Search
    astar, gen, exp, edges, order = astar_search_with_log(problem) # Make sure astar_search returns 5 items
    print_path_trace(astar, "A* Search", False)
    draw_search_tree(gen, exp, edges, order, "astar_tree", solution_node=astar) # <-- Pass the solution node

    