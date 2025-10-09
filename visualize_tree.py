from graphviz import Digraph
from collections import defaultdict
from typing import Iterable, List, Tuple, Optional, Any, Set
import argparse
import os

# Import search components
from DrillingRobot import DrillingRobot
from search import breadth_first_graph_search, depth_first_graph_search, astar_search


def visualize_tree(
    gen: Iterable[Any],
    exp: Iterable[Any],
    edges: Iterable[Tuple[Any, Any]],
    node_list_in_order: Iterable[Any],
    filename: str,
    solution_node: Optional[Any] = None,
) -> None:
    """
    Render a search tree/graph as a layered diagram using Graphviz.

    Coloring:
        lightgreen = nodes in the solution path
        lightcoral = expanded nodes
        lightblue = generated nodes (not expanded)
    """

    # Map each state to its Node object
    state_to_node = {n.state: n for n in gen}

    dot = Digraph(
        comment="Search Tree",
        graph_attr={
            "rankdir": "TB",
            "splines": "polyline",
            "overlap": "false",
            "dpi": "150",
            "ranksep": "1.5",
            "nodesep": "0.7",
            "concentrate": "false",
        },
        node_attr={
            "shape": "box",
            "width": "2.2",
            "height": "0.9",
            "fixedsize": "true",
            "style": "filled",
            "fontsize": "12",
        },
        edge_attr={
            "fontsize": "13",
            "labelfloat": "true",
            "labeldistance": "2.5",
            "labelangle": "-20",
        },
    )

    # Identify sets of states
    solution_states: Set[Any] = set()
    if solution_node is not None and hasattr(solution_node, "path"):
        try:
            solution_states = {n.state for n in solution_node.path()}
        except Exception:
            solution_states = set()

    expanded_states = {n.state for n in exp}
    ordered_depth_groups = defaultdict(list)

    # Add nodes
    for item in node_list_in_order:
        node_state = getattr(item, "state", item)
        node = state_to_node.get(node_state)
        if node is None:
            continue

        if node_state in solution_states:
            fill = "lightgreen"
        elif node_state in expanded_states:
            fill = "lightcoral"
        else:
            fill = "lightblue"

        expansion_order = getattr(node, "expansion_order", "?")
        depth = getattr(node, "depth", "?")
        path_cost = getattr(node, "path_cost", 0.0)
        label = f"#{expansion_order}\nS: {node.state}\nd: {depth}\ng(n): {path_cost:.1f}"

        node_key = str(node.state)
        dot.node(node_key, label=label, fillcolor=fill)
        ordered_depth_groups[depth].append(node_key)

    # Add edges
    for parent, child in edges:
        p_state = getattr(parent, "state", parent)
        c_state = getattr(child, "state", child)
        action = getattr(child, "action", None)
        dot.edge(str(p_state), str(c_state), label=str(action) if action else "")

    # Render
    dot.render(filename, format="png", cleanup=True)
    print(f"Search tree saved to {filename}.png")


if __name__ == "__main__":
    # ---------------------------------
    # Command-line argument parsing
    # ---------------------------------
    parser = argparse.ArgumentParser(
        description="Generate and visualize a search tree for the DrillingRobot problem."
    )
    parser.add_argument(
        "map_path",
        type=str,
        help="Path to the input map file (required)."
    )
    parser.add_argument(
        "-a", "--algorithm",
        type=str,
        required=True,
        choices=["bfs", "dfs", "astar"],
        help="The search algorithm to run (bfs, dfs, or astar)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        required=True,
        help="Output file name (without extension). Default: tree_output"
    )
    parser.add_argument(
        "--heuristic",
        type=str,
        default="default",
        help="Heuristic function to use with A* (optional)."
    )

    args = parser.parse_args()

    # ---------------------------------
    # Problem initialization
    # ---------------------------------
    map_path = args.map_path
    algorithm = args.algorithm.lower()
    heuristic = args.heuristic.lower()
    output_name = args.output

    if not os.path.exists(map_path):
        print(f"ERROR: Map file '{map_path}' not found.")
        exit(1)

    print(f"Loading problem from {map_path} ...")
    problem = DrillingRobot(map_path)

    # ---------------------------------
    # Run selected algorithm
    # ---------------------------------
    print(f"Running algorithm: {algorithm.upper()}")

    if algorithm == "bfs":
        sol, gen, exp, edges, order, frontier = breadth_first_graph_search(problem)
    elif algorithm == "dfs":
        sol, gen, exp, edges, order, frontier = depth_first_graph_search(problem)
    elif algorithm == "astar":
        if heuristic == "default":
            sol, gen, exp, edges, order, frontier = astar_search(problem)
        elif hasattr(problem, heuristic):
            heuristic_func = getattr(problem, heuristic)
            sol, gen, exp, edges, order, frontier = astar_search(problem, h=heuristic_func)
        else:
            print(f"Warning: Heuristic '{heuristic}' not found. Using default.")
            sol, gen, exp, edges, order, frontier = astar_search(problem)
    else:
        print("Invalid algorithm.")
        exit(1)

    # ---------------------------------
    # Draw search tree
    # ---------------------------------
    print(f"Generating search tree image for {algorithm.upper()} ...")
    visualize_tree(gen, exp, edges, order, output_name, sol)

    print("Done.")
