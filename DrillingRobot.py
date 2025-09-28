from search import *

class DrillingRobot(Problem):
    def __init__(self, file):
        # TODO: Leer del archivo la matriz
        map=[]
        initial=()
        goal=()
        with open(file, 'r') as f:
            line =f.readline()
            parts=line.split()
            
            
        self.map = # Matriz resultante de leer el archivo
        self.initial=(3,3,1)
        self.goal=(2,3,5)
        super().__init__(initial, goal)

    def actions(self, state):
        """Return the actions that can be executed in the given
        state. The result would typically be a list, but if there are
        many actions, consider yielding them one at a time in an
        iterator, rather than building them all at once."""
        

        # At the beginig we asume that the 'drill' action is not possible
        possible_actions = ['TURN_LEFT', 'TURN_RIGHT']

        x, y, orientation = state
        
        # Assign to each orientation the change in the coordinates (dx, dy) if the robot execute the 'drill' action
        move_deltas = {
            0: (-1, 0),  # North
            1: (-1, 1),  # Northeast
            2: (0, 1),   # East
            3: (1, 1),   # Southeast
            4: (1, 0),   # South
            5: (1, -1),  # Southwest
            6: (0, -1),  # West
            7: (-1, -1)  # Northwest
        }
        
        # Apply the change in the coordinates
        dx, dy = move_deltas[orientation]
        new_x, new_y = x + dx, y + dy
        
        # Verify if its possible to drill (map limits)
        if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
            possible_actions.append('DRILL')
            
        return possible_actions

    def result(self, state, action):
        """Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state)."""
        
        if action == 'TURN_LEFT':
            state[2] -= 1
        elif action == 'TURN_RIGHT':
            state[2] += 1

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
            # Orientación a cambio de coordenadas
            move_deltas = {
                0: (-1, 0),  # North
                1: (-1, 1),  # Northeast
                2: (0, 1),   # East
                3: (1, 1),   # Southeast
                4: (1, 0),   # South
                5: (1, -1),  # Southwest
                6: (0, -1),  # West
                7: (-1, -1)  # Northwest
            }
            dx, dy = move_deltas[orientation]
            new_x, new_y = x + dx, y + dy
            
            return (new_x, new_y, orientation)


    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal or checks for state in self.goal if it is a
        list, as specified in the constructor. Override this method if
        checking against a single self.goal is not enough."""
        if isinstance(self.goal, list):
            return is_in(state, self.goal)
        else:
            return state == self.goal
        
    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2. If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1
        
    
def path_actions(node):
    "The sequence of actions to get to this node."
    if node.parent is None:
        return []  
    return path_actions(node.parent) + [node.action]

def path_states(node):
    "The sequence of states to get to this node."
    if node in (cutoff, failure, None): 
        return []
    return path_states(node.parent) + [node.state]
    



class EightPuzzle(Problem):
    """ The problem of sliding tiles numbered from 1 to 8 on a 3x3 board, where one of the
    squares is a blank. A state is represented as a tuple of length 9, where  element at
    index i represents the tile number  at index i (0 if it's an empty square) """

    def __init__(self, initial, goal=(1, 2, 3, 4, 5, 6, 7, 8, 0)):
        """ Define goal state and initialize a problem """
        super().__init__(initial, goal)

    def find_blank_square(self, state):
        """Return the index of the blank square in a given state"""

        return state.index(0)

    def actions(self, state):
        """ Return the actions that can be executed in the given state.
        The result would be a list, since there are only four possible actions
        in any given state of the environment """

        possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
        index_blank_square = self.find_blank_square(state)

        if index_blank_square % 3 == 0:
            possible_actions.remove('LEFT')
        if index_blank_square < 3:
            possible_actions.remove('UP')
        if index_blank_square % 3 == 2:
            possible_actions.remove('RIGHT')
        if index_blank_square > 5:
            possible_actions.remove('DOWN')

        return possible_actions

    def result(self, state, action):
        """ Given state and action, return a new state that is the result of the action.
        Action is assumed to be a valid action in the state """

        # blank is the index of the blank square
        blank = self.find_blank_square(state)
        new_state = list(state)

        delta = {'UP': -3, 'DOWN': 3, 'LEFT': -1, 'RIGHT': 1}
        neighbor = blank + delta[action]
        new_state[blank], new_state[neighbor] = new_state[neighbor], new_state[blank]

        return tuple(new_state)

    def goal_test(self, state):
        """ Given a state, return True if state is a goal state or False, otherwise """

        return state == self.goal

    def check_solvability(self, state):
        """ Checks if the given state is solvable """

        inversion = 0
        for i in range(len(state)):
            for j in range(i + 1, len(state)):
                if (state[i] > state[j]) and state[i] != 0 and state[j] != 0:
                    inversion += 1

        return inversion % 2 == 0

    def h(self, node):
        """ Return the heuristic value for a given state. Default heuristic function used is 
        h(n) = number of misplaced tiles """

        return sum(s != g for (s, g) in zip(node.state, self.goal))
