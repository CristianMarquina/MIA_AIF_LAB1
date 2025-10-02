from search import *

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
        possible_actions = ['TURN_LEFT', 'TURN_RIGHT']

        x, y, orientation = state
        
        # Apply the change in the coordinates
        dx, dy = self.orientation_map[orientation]
        new_x, new_y = x + dx, y + dy
        
        # Verify if its possible to drill (map limits)
        if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
            possible_actions.append('DRILL')
            
        return possible_actions
    

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""

        x, y, orientation = state

        if action == 'TURN_LEFT':
            # New orientation between 0 and 7
            new_orientation = (orientation - 1) % 8
            return (x, y, new_orientation)
        
        elif action == 'TURN_RIGHT':
            # New orientation between 0 and 7
            new_orientation = (orientation + 1) % 8
            return (x, y, new_orientation)
        
        elif action == 'DRILL':
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

        if action == 'TURN_LEFT' or action == 'TURN_RIGHT':
            return c + 1
        
        elif action == 'DRILL':
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
        
