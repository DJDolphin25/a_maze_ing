# mazegen/generator.py
import random
from typing import List, Tuple
from .cells import Cell, Wall


class MazeGenerator:
    """Generates a perfect maze (with no loops) on a width x height grid
    using an explicit stack for backtracking.

    """

    def __init__(self, width: int, height: int, seed: int | None = None):
        self.width = width
        self.height = height
        self.rng = random.Random(seed)

        self.grid: List[List[Cell]] = [
            [Cell(x, y) for x in range(width)] for y in range(height)
        ]

    def _get_unvisited_neighbors(
        self, current_cell: Cell
    ) -> List[Tuple[Cell, Wall]]:
        """Finds the neighbor cells of 'current_cell' that have not been
        visited yet, and returns them together with the wall that separates
        them from 'current_cell'.

        We only look at neighbors that are not visited yet. This is the key
        rule that makes sure the final maze has no loops: every cell in the
        maze gets connected to exactly one path, with no cycles.
        Because of this rule, the number of open walls will always be equal to
        (number of cells - 1).

        Args:
            current_cell: the cell we're looking around.

        Returns:
            A list of (neighbor_cell, wall_direction) pairs, one per
            unvisited neighbor, where wall_direction is the wall on
            current_cell's side that separates it from that neighbor.
        """
        neighbors: List[Tuple[Cell, Wall]] = []
        directions = [
            (0, -1, Wall.NORTH),  # UP
            (1, 0, Wall.EAST),    # RIGHT
            (0, 1, Wall.SOUTH),   # DOWN
            (-1, 0, Wall.WEST)    # LEFT
        ]

        for move_x, move_y, wall_dir in directions:
            # Coordinates of the neighbor = current coordinates + movement
            neighbor_x = current_cell.x + move_x
            neighbor_y = current_cell.y + move_y

            # Is the neighbor within the limits of the whole grid?
            if 0 <= neighbor_x < self.width and 0 <= neighbor_y < self.height:
                neighbor_cell = self.grid[neighbor_y][neighbor_x]

                # Has the neighbor been visited?
                if not neighbor_cell.visited:
                    neighbors.append((neighbor_cell, wall_dir))

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

        Args:
            start_x: column of the cell where generation begins.
            start_y: row of the cell where generation begins.

        Returns:
            None. The maze is built in place by opening walls on the
            cells already stored in self.grid.
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
                stack.pop()  # Backtrack / Go back, this path is finished
