from search import *
from drilling_utils import *
from math import sqrt

class DrillingRobot(Problem):
    def __init__(self, file):
        """Initializes the problem state from a given map file.
        This constructor reads a text file that defines the terrain,
        dimensions, initial state, and goal state for the drilling robot
        problem.

        Args:
            file (str): The path to the input map file. 
        """
        with open(file, 'r') as f:
            line =f.readline()
            parts=line.split()
            self.rows, self.cols = map(int, parts)
            self.map = []
            for _ in range(self.rows):
                line = f.readline()
                row_of_numbers = list(map(int, line.strip().split()))
                self.map.append(row_of_numbers)

            self.min_hardness = min(min(row) for row in self.map)

            line = f.readline()
            initial_state = tuple(map(int, line.strip().split()))

            line = f.readline()
            goal_state = tuple(map(int, line.strip().split()))

        super().__init__(initial_state, goal_state)
        # Orientación a cambio de coordenadas
        self.orientation_map = {
            0: (-1, 0),  # North
            1: (-1, 1),  # Northeast
            2: (0, 1),   # East
            3: (1, 1),   # Southeast
            4: (1, 0),   # South
            5: (1, -1),  # Southwest
            6: (0, -1),  # West
            7: (-1, -1)  # Northwest
        }


    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        

        # At the beginig we asume that the 'drill' action is not possible
        possible_actions = [TURN_LEFT, TURN_RIGHT]

        x, y, orientation = state
        
        # Apply the change in the coordinates
        dx, dy = self.orientation_map[orientation]
        new_x, new_y = x + dx, y + dy
        
        # Verify if its possible to drill (map limits)
        if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
            possible_actions.append(DRILL)
            
        return possible_actions
    

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        x, y, orientation = state

        if action == TURN_LEFT:
            # New orientation between 0 and 7
            new_orientation = (orientation - 1) % 8
            return (x, y, new_orientation)
        
        elif action == TURN_RIGHT:
            # New orientation between 0 and 7
            new_orientation = (orientation + 1) % 8
            return (x, y, new_orientation)
        
        elif action == DRILL:
            dx, dy = self.orientation_map[orientation]
            new_x, new_y = x + dx, y + dy
            
            return (new_x, new_y, orientation)


    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""

        x, y, orientation = state
        
        # El objetivo (self.goal) es (xt, yt, ot)
        gx, gy, go = self.goal
        
        # 1. Comprobar si la posición (x, y) coincide
        is_at_goal_location = (x == gx and y == gy)
        
        # 2. Comprobar la orientación:
        # Es válida si: ot es 8 (irrelevante) O la orientación actual coincide con ot.
        is_orientation_ok = (go == 8 or orientation == go)
        
        return is_at_goal_location and is_orientation_ok
        
        
    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2. If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""

        if action == TURN_LEFT or action == TURN_RIGHT:
            return c + 1
        
        elif action == DRILL:
            new_x, new_y, _ = state2
            # La dureza de la roca es el valor en la matriz del mapa
            return c + self.map[new_x][new_y]
        
        return c
    
    def h(self, node):
        """ Return the heuristic value for a given state. Default heuristic function used is 
        the Manhattan distance """

        x, y, _ = node.state
        gx, gy, _ = self.goal

        return abs(x - gx) + abs(y - gy)
    
    def h_chebyshev(self, node):
        x, y, _ = node.state
        gx, gy, _ = self.goal
        return max(abs(x - gx), abs(y - gy))
    
    def h_euclidean(self, node):
        x, y, _ = node.state
        gx, gy, _ = self.goal
        return sqrt((x - gx)**2 + (y - gy)**2)
    
    def h_minhardness(self, node):
        x, y, _ = node.state
        gx, gy, _ = self.goal
        chebyshev = max(abs(x - gx), abs(y - gy))
        return chebyshev * self.min_hardness
    
    def h_combined(self, node):
        """
        Combined heuristic: (Chebyshev distance * min_hardness) + orientation adjustment.
        
        - The first term estimates the minimum drilling cost assuming each move
        costs at least the minimum rock hardness value in the map.
        - The second term adds a lower bound on the number of turns required,
        considering both the current and goal orientations.
        
        This heuristic is admissible and suitable for 8-directional movement
        with rotation cost = 1 and drilling cost >= min_hardness.
        """
        x, y, o = node.state
        gx, gy, go = self.goal

        # --- 1) Drilling cost lower bound (Chebyshev * min hardness) ---
        dx, dy = gx - x, gy - y
        adx, ady = abs(dx), abs(dy)
        chebyshev = max(adx, ady)
        drill_lb = chebyshev * self.min_hardness

        # Early return if already at goal position
        if adx == 0 and ady == 0:
            if go == 8:  # orientation irrelevant
                return 0
            diff = abs(o - go) % 8
            return min(diff, 8 - diff)

        # --- 2) Orientation adjustment (turns) ---
        # Minimal turns to align with a direction that moves closer to goal
        turn_dist = lambda a, b: min((a - b) % 8, (b - a) % 8)
        sgn = lambda v: (v > 0) - (v < 0)

        # Possible progress direction(s)
        sx, sy = sgn(dx), sgn(dy)
        if adx > ady:
            progress_dirs = [(sx, 0)]
        elif ady > adx:
            progress_dirs = [(0, sy)]
        else:
            progress_dirs = [(sx, sy)]

        # Map (signs) → orientation index
        dir_map = {
            (-1,  0): 0, (-1,  1): 1, (0, 1): 2, (1, 1): 3,
            (1,  0): 4, (1, -1): 5, (0, -1): 6, (-1, -1): 7
        }

        # Minimum turns to start progressing
        turns_now = min(turn_dist(o, dir_map[d]) for d in progress_dirs)

        # Minimum turns required at goal (if orientation matters)
        if go == 8:
            turns_end = 0
        else:
            last_dirs = progress_dirs  # same idea: direction of last move
            turns_end = min(turn_dist(go, dir_map[d]) for d in last_dirs)

        turns_lb = max(turns_now, turns_end)

        # --- 3) Final combined heuristic ---
        return drill_lb + turns_lb

    
    def h2(self, node):
        """
        Heuristic = (Chebyshev distance * min_hardness) + orientation lower bound,
        where the orientation term is max(turns_to_start_progress, turns_needed_at_goal).
        """
        x, y, o = node.state
        gx, gy, go = self.goal

        dx, dy = gx - x, gy - y
        adx, ady = abs(dx), abs(dy)

        # --- Drilling lower bound (Chebyshev steps * min hardness) ---
        chebyshev = max(adx, ady)
        drill_lb = chebyshev * self.min_hardness

        # Early exit if already at goal cell
        if chebyshev == 0:
            # If a specific final orientation is required, pay turns to align; else 0
            if go == 8:
                return 0
            # turn distance without helpers
            diff = abs(o - go) % 8
            turns = min(diff, 8 - diff)
            return turns

        # Local helpers (lambdas) to avoid extra methods
        turn_dist = lambda a, b: min((a - b) % 8, (b - a) % 8)
        sgn = lambda v: (v > 0) - (v < 0)

        # Map (sign(dx), sign(dy)) -> orientation index (same convention as orientation_map)
        dir_from_signs = {
            (-1,  0): 0,  # N
            (-1,  1): 1,  # NE
            ( 0,  1): 2,  # E
            ( 1,  1): 3,  # SE
            ( 1,  0): 4,  # S
            ( 1, -1): 5,  # SW
            ( 0, -1): 6,  # W
            (-1, -1): 7,  # NW
        }

        sx, sy = sgn(dx), sgn(dy)

        # --- Directions that reduce Chebyshev on the next step (progress dirs) ---
        progress_dirs = set()
        if adx > ady:
            progress_dirs.add(dir_from_signs[(sgn(dx), 0)])
        elif ady > adx:
            progress_dirs.add(dir_from_signs[(0, sgn(dy))])
        else:  # adx == ady != 0 -> only the exact diagonal reduces Chebyshev
            progress_dirs.add(dir_from_signs[(sx, sy)])

        # Minimum turns to start progressing from current orientation
        turns_now = min(turn_dist(o, d) for d in progress_dirs) if progress_dirs else 0

        # --- Turns needed at the end (if goal orientation is constrained) ---
        if go == 8:
            turns_end = 0
        else:
            # Possible orientations for the LAST step to land exactly on (gx, gy)
            last_dirs = set()
            if adx > ady:
                last_dirs.add(dir_from_signs[(sgn(dx), 0)])
            elif ady > adx:
                last_dirs.add(dir_from_signs[(0, sgn(dy))])
            else:
                last_dirs.add(dir_from_signs[(sx, sy)])

            # If for some reason no last_dirs (shouldn't happen here), fall back to aligning at end
            if last_dirs:
                turns_end = min(turn_dist(go, d) for d in last_dirs)
            else:
                turns_end = turn_dist(o, go)

        turns_lb = max(turns_now, turns_end)

        return drill_lb + turns_lb
        
