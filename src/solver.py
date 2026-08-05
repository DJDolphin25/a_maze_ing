# src/solver.py
"""Solves the maze: finds the shortest path from entry to exit using BFS."""
from collections import deque
from typing import List, Tuple, Dict
from .cells import Cell, Wall


def solve_bfs(grid: List[List[Cell]], entry: Tuple[int, int], exit: Tuple[int, int]) -> str:
    """Finds the shortest path from entry to exit and returns it as a string of 'N', 'E', 'S', 'W'.

    BFS explores the maze one step at a time, spreading out evenly in every
    direction, so the first time we reach the exit we know it's by the
    shortest possible path (since every move costs the same). While we
    explore, 'parent' remembers, for each cell we visit, which cell we came
    from and which move got us there. Once we reach the exit, we can walk
    this dictionary backwards to rebuild the whole path.
    """
    start_cell = grid[entry[1]][entry[0]]
    target_cell = grid[exit[1]][exit[0]]

    queue = deque([start_cell])
    parent: Dict[Cell, Tuple[Cell, str]] = {}
    visited = {start_cell}

    moves = [
        (0, -1, Wall.NORTH, 'N'),
        (1, 0, Wall.EAST, 'E'),
        (0, 1, Wall.SOUTH, 'S'),
        (-1, 0, Wall.WEST, 'W')
    ]

    while queue:
        curr = queue.popleft()
        if curr == target_cell:
            break

        for dx, dy, wall_flag, char_dir in moves:
            # We can only move that way if there is NO wall blocking us.
            if not curr.has_wall(wall_flag):
                nx, ny = curr.x + dx, curr.y + dy
                neighbor = grid[ny][nx]
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = (curr, char_dir)
                    queue.append(neighbor)

    # Rebuild the path: start at target_cell and keep following 'parent'
    # backwards until we reach start_cell (which has no entry in the dict,
    # since it's where we began). Then reverse the moves so the path reads
    # from entry to exit instead of exit to entry.
    path_chars = []
    curr = target_cell
    while curr in parent:
        prev, move_char = parent[curr]
        path_chars.append(move_char)
        curr = prev

    return "".join(reversed(path_chars))
