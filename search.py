from collections import deque
from search_utils import *


class Problem:
    """Abstract base class for a formal problem.

    Subclass this class and implement at least the methods `actions` and `result`.
    Optionally, you may override `__init__`, `goal_test`, and `path_cost`.
    Then, you can create instances of your subclass and solve them with any of
    the provided search algorithms.
    """

    def __init__(self, initial, goal=None):
        """Constructor that defines the initial state and, optionally, a goal state."""
        self.initial = initial
        self.goal = goal

    def actions(self, state):
        """Return the set of possible actions that can be executed in a given state."""
        raise NotImplementedError

    def result(self, state, action):
        """Return the state that results from executing the given action in the given state."""
        raise NotImplementedError

    def goal_test(self, state):
        """Return True if the given state is a goal state.

        By default, compares the state to self.goal or checks for membership
        if the goal is defined as a list.
        """
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal

    def path_cost(self, c, state1, action, state2):
        """Return the cost of reaching `state2` from `state1` via `action`,
        given an accumulated cost `c` up to `state1`.

        The default implementation adds 1 per transition.
        """
        return c + 1

    def value(self, state):
        """Return the value of a state for optimization problems (e.g., hill climbing)."""
        raise NotImplementedError


# ______________________________________________________________________________


class Node:
    """Represents a node in a search tree.

    Each node contains:
      - a reference to its parent (the node that generated it)
      - the state it represents
      - the action used to reach it
      - the total path cost (g) to this node

    If a state is reached through multiple paths, there will be multiple nodes
    with the same state but different path costs or parent references.
    """

    def __init__(self, state, parent=None, action=None, path_cost=0):
        """Create a new search tree node derived from a parent via an action."""
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost
        self.depth = 0
        if parent:
            self.depth = parent.depth + 1

        # Record of the order in which the node was expanded (for tracing)
        self.expansion_order = 0

    def __repr__(self):
        return "<Node {}>".format(self.state)

    def __lt__(self, node):
        return self.state < node.state

    def expand(self, problem):
        """Return a list of successor nodes reachable from this node in one step."""
        return [self.child_node(problem, action)
                for action in problem.actions(self.state)]

    def child_node(self, problem, action):
        """Generate a child node by applying an action to the current state."""
        next_state = problem.result(self.state, action)
        next_node = Node(next_state, self, action, problem.path_cost(self.path_cost, self.state, action, next_state))
        return next_node

    def solution(self):
        """Return the list of actions that lead from the root to this node."""
        return [node.action for node in self.path()[1:]]

    def path(self):
        """Return the sequence of nodes from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    # Nodes with the same state are treated as equal for queue management.
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        # Use the hash of the state for fast lookup and comparison.
        return hash(self.state)


def depth_first_graph_search(problem):
    """
    Depth-First Search (DFS) for graph-based problems.

    Returns
    -------
    (solution, generated, expanded, edges, node_list_in_order, frontier)
        solution : Node or None
            Solution node if the goal is found; None otherwise.
        generated : set[Node]
            Set of all generated nodes.
        expanded : set[Node]
            Set of expanded nodes (whose successors were explored).
        edges : list[tuple(Node, Node)]
            List of (parent, child) edges created.
        node_list_in_order : list[Node]
            Nodes ordered by generation (for visualization).
        frontier : list[Node]
            Final stack (frontier) at termination.
    """
    node = Node(problem.initial)

    # Tracking structures
    expanded = set()
    generated = {node}
    edges = []
    node_list_in_order = [node]
    counter = 1
    node.expansion_order = 0

    if problem.goal_test(node.state):
        return node, generated, expanded, edges, node_list_in_order, []

    frontier = [node]                 # Stack
    frontier_states = {node.state}    # States currently in frontier
    explored = set()                  # States already expanded

    while frontier:
        node = frontier.pop()
        frontier_states.remove(node.state)

        if node.state in explored:
            continue
        explored.add(node.state)
        expanded.add(node)

        for child in node.expand(problem):
            s = child.state
            if (s not in explored) and (s not in frontier_states):
                generated.add(child)
                edges.append((node, child))
                child.expansion_order = counter
                counter += 1
                node_list_in_order.append(child)

                if problem.goal_test(s):
                    return child, generated, expanded, edges, node_list_in_order, frontier

                frontier.append(child)
                frontier_states.add(s)

    # If no solution is found, return all collected data and the final (empty) frontier
    return None, generated, expanded, edges, node_list_in_order, frontier


def breadth_first_graph_search(problem):
    """Breadth-First Search (BFS) for graph-based problems. [Figure 3.11]

    This version maintains the order of generated nodes (FIFO)
    for accurate visualization of the search tree.
    """
    node = Node(problem.initial)
    node_list_in_order = [node]

    if problem.goal_test(node.state):
        # If the initial state is the goal, return immediately.
        return node, {node}, set(), [], node_list_in_order, frontier

    frontier = deque([node])
    explored = set()
    generated = {node}
    expanded = set()
    edges = []
    expansion_order = {}
    counter = 1

    while frontier:
        node = frontier.popleft()
        expanded.add(node)
        explored.add(node.state)
        for child in node.expand(problem):

            # Check if the child is already in the frontier
            is_in_frontier = any(n.state == child.state for n in frontier)

            if child.state not in explored and not is_in_frontier:
                generated.add(child)
                edges.append((node, child))
                expansion_order[(node, child)] = counter
                counter += 1

                # Keep nodes in generation order (FIFO)
                node_list_in_order.append(child)

                if problem.goal_test(child.state):
                    return child, generated, expanded, edges, node_list_in_order, frontier
                frontier.append(child)

    return None, generated, expanded, edges, node_list_in_order, frontier


def best_first_graph_search(problem, f):
    """
    Best-First Search.

    Expands the node with the smallest value of f(node).

    Parameters
    ----------
    problem : Problem
        Problem instance.
    f : callable
        Evaluation function. Smaller f values indicate higher priority.
        Examples:
          - Greedy Best-First: f = lambda n: h(n)
          - A*: f = lambda n: n.path_cost + h(n)

    Returns
    -------
    (solution, generated, expanded, edges, node_list_in_order, frontier)
    """
    f = memoize(f, 'f')
    node = Node(problem.initial)

    # Tracking structures
    expanded = set()
    generated = {node}
    edges = []
    node_list_in_order = [node]
    counter = 1
    node.expansion_order = 0

    frontier = PriorityQueue('min', f)
    frontier.append(node)
    explored = set()

    while frontier:
        node = frontier.pop()

        if problem.goal_test(node.state):
            # Return the frontier as a list sorted by priority
            return node, generated, expanded, edges, node_list_in_order, [item for _, item in sorted(frontier.heap)]

        expanded.add(node)
        explored.add(node.state)

        for child in node.expand(problem):
            s = child.state
            if (s not in explored) and (child not in frontier):
                generated.add(child)
                edges.append((node, child))
                child.expansion_order = counter
                counter += 1
                node_list_in_order.append(child)
                frontier.append(child)
            elif child in frontier:
                # Update the node if a better (lower) f value is found
                if f(child) < frontier[child]:
                    del frontier[child]
                    frontier.append(child)

    # If no solution is found, return all recorded data
    return None, generated, expanded, edges, node_list_in_order, [item for _, item in sorted(frontier.heap)]


def astar_search(problem, h=None):
    """A* Search: Best-First Search with f(n) = g(n) + h(n).

    The heuristic function h must be provided either when calling this function
    or as part of the Problem subclass.
    """
    h = memoize(h or problem.h, 'h')
    return best_first_graph_search(problem, lambda n: n.path_cost + h(n))
