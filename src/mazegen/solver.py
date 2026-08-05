# mazegen/solver.py
from collections import deque
from typing import List, Tuple, Dict
from .cells import Cell, Wall


def solve_bfs(
    grid: List[List[Cell]],
    entry: Tuple[int, int],
    exit: Tuple[int, int],
) -> str:
    """Finds the shortest path from entry to exit and returns it as a string
    of 'N', 'E', 'S', 'W'.

    BFS explores the maze one step at a time, spreading out evenly in every
    direction, so the first time we reach the exit we know it's by the
    shortest possible path (since every move costs the same). While we
    explore, 'parent' remembers, for each cell we visit, which cell we came
    from and which move got us there. Once we reach the exit, we can walk
    this dictionary backwards to rebuild the whole path.

    Args:
        grid: the maze, as a list of rows of Cell.
        entry: (x, y) coordinates of the starting cell.
        exit: (x, y) coordinates of the target cell.

    Returns:
        The shortest path from entry to exit as a string of 'N', 'E',
        'S', 'W' moves, in order. Empty string if exit is unreachable.
    """
    start_cell = grid[entry[1]][entry[0]]
    exit_cell = grid[exit[1]][exit[0]]

    queue = deque([start_cell])
    parent: Dict[Cell, Tuple[Cell, str]] = {}  # Stores the path
    visited = {start_cell}

    moves = [
        (0, -1, Wall.NORTH, 'N'),  # UP
        (1, 0, Wall.EAST, 'E'),    # RIGHT
        (0, 1, Wall.SOUTH, 'S'),   # DOWN
        (-1, 0, Wall.WEST, 'W')    # LEFT
    ]

    while queue:
        current_cell = queue.popleft()
        if current_cell == exit_cell:
            break

        for move_x, move_y, wall_dir, move_char in moves:

            # We can only move that way if there is NO wall blocking us
            if not (current_cell.walls & wall_dir):
                neighbor_x = current_cell.x + move_x
                neighbor_y = current_cell.y + move_y
                neighbor_cell = grid[neighbor_y][neighbor_x]

                if neighbor_cell not in visited:
                    visited.add(neighbor_cell)
                    parent[neighbor_cell] = (current_cell, move_char)
                    queue.append(neighbor_cell)

    # Rebuild the path: start at the exit_cell and keep following 'parent'
    # backwards until we reach start_cell (which has no entry in the dict,
    # since it's where we began). Then reverse the moves so the path reads
    # from entry to exit instead of exit to entry
    path_chars = []
    current_cell = exit_cell
    while current_cell in parent:
        prev_cell, move_char = parent[current_cell]
        path_chars.append(move_char)
        current_cell = prev_cell

    return "".join(reversed(path_chars))
