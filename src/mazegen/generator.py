# mazegen/generator.py
import random
from typing import List, Tuple
from .cells import Cell, Wall


class MazeGenerator:
    """Genera un laberinto perfecto (spanning tree sin ciclos) sobre una
    rejilla width x height, usando backtracking con pila explícita."""

    def __init__(self, width: int, height: int, seed: int | None = None):
        self.width = width
        self.height = height
        self.rng = random.Random(seed)

        self.grid: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]

    def _get_unvisited_neighbors(self, cell: Cell) -> List[Tuple[Cell, Wall]]:
        """Finds the neighbor cells of 'cell' that have not been visited yet,
        and returns them together with the wall that separates them from
        'cell'.

        We only look at neighbors that are not visited yet. This is the key
        rule that makes sure the final maze has no loops: every cell in the
        maze gets connected to exactly one path, with no cycles.
        Because of this rule, the number of open walls will always be equal to
        (number of cells - 1).
        """
        neighbors: List[Tuple[Cell, Wall]] = []
        directions = [
            (0, -1, Wall.NORTH),
            (1, 0, Wall.EAST),
            (0, 1, Wall.SOUTH),
            (-1, 0, Wall.WEST)
        ]

        for dx, dy, wall_dir in directions:
            nx, ny = cell.x + dx, cell.y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbor = self.grid[ny][nx]
                if not neighbor.visited:
                    neighbors.append((neighbor, wall_dir))
        return neighbors

    def generate_perfect(self, start_x: int = 0, start_y: int = 0) -> None:
        """Builds a perfect maze (no loops, every cell reachable) using a
        stack instead of real function recursion.

        We use a stack (a simple list we add to and remove from) instead of
        calling the function again and again on itself. This avoids a
        Python error (RecursionError) that happens when a function calls
        itself too many times, which can happen on big mazes.
        Each time we add a cell to the stack, it's like moving forward
        into a new cell. Each time we remove a cell from the stack, it's
        like going back because there's nowhere new left to go from there.
        """
        stack: List[Cell] = []
        start_cell = self.grid[start_y][start_x]
        start_cell.visited = True
        stack.append(start_cell)

        while stack:
            current = stack[-1]
            neighbors = self._get_unvisited_neighbors(current)

            if neighbors:
                next_cell, wall_dir = self.rng.choice(neighbors)
                # Remove the wall between the two cells, on both sides.
                # Uses Cell.remove_wall() instead of touching .walls directly,
                # so the bit manipulation stays in one place (see cells.py).
                current.remove_wall(wall_dir)
                next_cell.remove_wall(Wall.opposite(wall_dir))

                next_cell.visited = True
                stack.append(next_cell)
            else:
                stack.pop()  # Backtrack || Go back, this path is finished
