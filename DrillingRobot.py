from math import sqrt
from typing import List, Tuple

from search import Problem
from drilling_utils import TURN_LEFT, TURN_RIGHT, DRILL


class DrillingRobot(Problem):
    """
    Drilling robot search problem on a weighted 8-connected grid.

    Input file format:
      - First line: "rows cols"
      - Next `rows` lines: integer hardness values per cell (drill cost)
      - Next line: "x0 y0 o0"    (initial state)
      - Next line: "xt yt ot"    (goal state; ot=8 means orientation irrelevant)

    State representation: (x, y, o)
      - x, y: grid coordinates (0-indexed, row-major)
      - o: orientation in {0..7}:
           0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW
    """

    def __init__(self, file: str):
        """
        Load the map, initial state, and goal from file and initialize the problem.

        Args:
            file: Path to the input map file.
        """
        with open(file, "r") as f:
            # Grid size
            parts = f.readline().split()
            self.rows, self.cols = map(int, parts)

            # Terrain hardness (drill costs)
            self.map: List[List[int]] = []
            for _ in range(self.rows):
                row = list(map(int, f.readline().strip().split()))
                self.map.append(row)

            # Minimum hardness over the entire map (used by heuristics)
            self.min_hardness = min(min(row) for row in self.map)

            # Initial and goal states
            initial_state = tuple(map(int, f.readline().strip().split()))
            goal_state = tuple(map(int, f.readline().strip().split()))

        super().__init__(initial_state, goal_state)

        # Orientation index → (dx, dy)
        self.orientation_map = {
            0: (-1, 0),   # North
            1: (-1, 1),   # Northeast
            2: (0, 1),    # East
            3: (1, 1),    # Southeast
            4: (1, 0),    # South
            5: (1, -1),   # Southwest
            6: (0, -1),   # West
            7: (-1, -1),  # Northwest
        }

    def actions(self, state: Tuple[int, int, int]):
        """
        Return the set of applicable actions at `state`.

        Available actions:
          - TURN_LEFT, TURN_RIGHT: always applicable
          - DRILL: only if the forward cell (given current orientation) is inside the grid
                   (terrain cost is considered in `path_cost`, not here).
        """
        x, y, o = state
        actions = [TURN_LEFT, TURN_RIGHT]

        dx, dy = self.orientation_map[o]
        nx, ny = x + dx, y + dy

        # DRILL only if the next cell is within bounds
        if 0 <= nx < self.rows and 0 <= ny < self.cols:
            actions.append(DRILL)

        return actions

    def result(self, state: Tuple[int, int, int], action: str) -> Tuple[int, int, int]:
        """
        Apply `action` to `state` and return the resulting state.

        TURN_LEFT / TURN_RIGHT: rotate in place (orientation wraps in [0..7]).
        DRILL: advance one cell forward (orientation unchanged).
        """
        x, y, o = state

        if action == TURN_LEFT:
            return (x, y, (o - 1) % 8)

        if action == TURN_RIGHT:
            return (x, y, (o + 1) % 8)

        if action == DRILL:
            dx, dy = self.orientation_map[o]
            return (x + dx, y + dy, o)

        # No-op fallback (should not be reached if actions() is respected)
        return state

    def goal_test(self, state: Tuple[int, int, int]) -> bool:
        """
        Return True if `state` satisfies the goal.

        Goal is (gx, gy, go). If go==8, goal orientation is irrelevant
        and only (x==gx and y==gy) must hold.
        """
        x, y, o = state
        gx, gy, go = self.goal

        at_goal_xy = (x == gx and y == gy)
        orientation_ok = (go == 8) or (o == go)
        return at_goal_xy and orientation_ok

    def path_cost(
        self,
        c: float,
        state1: Tuple[int, int, int],
        action: str,
        state2: Tuple[int, int, int],
    ) -> float:
        """
        Accumulate the path cost.

        Rotation costs 1 per turn. DRILL costs the hardness of the entered cell.
        """
        if action in (TURN_LEFT, TURN_RIGHT):
            return c + 1

        if action == DRILL:
            x2, y2, _ = state2
            return c + self.map[x2][y2]

        return c  # Fallback

    # ----------------------------
    # Heuristics for A* (optional)
    # ----------------------------

    def h(self, node) -> float:
        """Manhattan distance to the goal position (ignores orientation and terrain)."""
        x, y, _ = node.state
        gx, gy, _ = self.goal
        return abs(x - gx) + abs(y - gy)

    def h_chebyshev(self, node) -> float:
        """Chebyshev distance (8-connected movement; ignores terrain)."""
        x, y, _ = node.state
        gx, gy, _ = self.goal
        return max(abs(x - gx), abs(y - gy))

    def h_euclidean(self, node) -> float:
        """Euclidean distance (continuous straight-line; ignores terrain)."""
        x, y, _ = node.state
        gx, gy, _ = self.goal
        return sqrt((x - gx) ** 2 + (y - gy) ** 2)

    def h_minhardness(self, node) -> float:
        """
        Lower bound on drilling cost:
        Chebyshev distance times the minimum hardness found in the map.
        """
        x, y, _ = node.state
        gx, gy, _ = self.goal
        cheb = max(abs(x - gx), abs(y - gy))
        return cheb * self.min_hardness

    def h_combined(self, node) -> float:
        """
        Combined heuristic = (Chebyshev * min_hardness) + turns lower bound.

        - Chebyshev * min_hardness: lower bound on total drilling cost
          (each forward move costs at least `min_hardness`).
        - Turns LB: minimal number of 45° rotations needed to align with a
          direction that reduces the Chebyshev distance; also considers goal
          orientation when it is relevant (go != 8).

        Admissible for 8-connected movement with rotation cost = 1 and
        drilling cost >= min_hardness.
        """
        x, y, o = node.state
        gx, gy, go = self.goal

        # 1) Drilling lower bound
        dx, dy = gx - x, gy - y
        adx, ady = abs(dx), abs(dy)
        cheb = max(adx, ady)
        drill_lb = cheb * self.min_hardness

        # Already at goal location: only orientation may matter
        if adx == 0 and ady == 0:
            if go == 8:
                return 0.0
            diff = abs(o - go) % 8
            return float(min(diff, 8 - diff))

        # 2) Minimal required turns
        turn_dist = lambda a, b: min((a - b) % 8, (b - a) % 8)
        sgn = lambda v: (v > 0) - (v < 0)

        # Preferred progress directions (those that strictly reduce Chebyshev)
        sx, sy = sgn(dx), sgn(dy)
        if adx > ady:
            progress_dirs = [(sx, 0)]
        elif ady > adx:
            progress_dirs = [(0, sy)]
        else:
            progress_dirs = [(sx, sy)]

        dir_map = {
            (-1, 0): 0,
            (-1, 1): 1,
            (0, 1): 2,
            (1, 1): 3,
            (1, 0): 4,
            (1, -1): 5,
            (0, -1): 6,
            (-1, -1): 7,
        }

        # Turns to start progressing from current heading
        turns_now = min(turn_dist(o, dir_map[d]) for d in progress_dirs)

        # Turns needed to finish with required goal orientation (if relevant)
        if go == 8:
            turns_end = 0
        else:
            turns_end = min(turn_dist(go, dir_map[d]) for d in progress_dirs)

        turns_lb = max(turns_now, turns_end)

        # 3) Final lower bound
        return float(drill_lb + turns_lb)
