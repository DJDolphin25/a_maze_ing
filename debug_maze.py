"""Rough manual check for day 4: generate a maze and print it as ASCII so
you can eyeball it, plus a few sanity checks (spanning tree + seed
reproducibility). Not the real terminal visualizer (that's a later day) —
just something quick to look at while developing.

Usage:
    python3 debug_maze.py [width] [height] [seed]
"""
import sys
from typing import List, Tuple

from src.cells import Cell, Wall
from src.generator import MazeGenerator


def print_maze(grid: List[List[Cell]], width: int, height: int) -> None:
    for y in range(height):
        # Top wall of this row
        top = ""
        for x in range(width):
            top += "+"
            top += "---" if grid[y][x].has_wall(Wall.NORTH) else "   "
        top += "+"
        print(top)

        # Cells + their west/east walls
        middle = ""
        for x in range(width):
            middle += "|" if grid[y][x].has_wall(Wall.WEST) else " "
            middle += "   "
        middle += "|" if grid[y][width - 1].has_wall(Wall.EAST) else " "
        print(middle)

    # Bottom wall of the whole maze
    bottom = ""
    for x in range(width):
        bottom += "+"
        bottom += "---" if grid[height - 1][x].has_wall(Wall.SOUTH) else "   "
    bottom += "+"
    print(bottom)


def check_spanning_tree(
    grid: List[List[Cell]], width: int, height: int
) -> Tuple[bool, int, int, bool]:
    all_visited = all(cell.visited for row in grid for cell in row)

    edges = 0
    for row in grid:
        for cell in row:
            if not cell.has_wall(Wall.NORTH):
                edges += 1
            if not cell.has_wall(Wall.WEST):
                edges += 1
    expected_edges = width * height - 1

    coherent = True
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            if x + 1 < width:
                right = grid[y][x + 1]
                if cell.has_wall(Wall.EAST) != right.has_wall(Wall.WEST):
                    coherent = False
            if y + 1 < height:
                down = grid[y + 1][x]
                if cell.has_wall(Wall.SOUTH) != down.has_wall(Wall.NORTH):
                    coherent = False

    return all_visited, edges, expected_edges, coherent


def main() -> None:
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    height = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 42

    gen = MazeGenerator(width, height, seed=seed)
    gen.generate_perfect()

    print(f"Maze {width}x{height}, seed={seed}\n")
    print_maze(gen.grid, width, height)

    all_visited, edges, expected_edges, coherent = check_spanning_tree(
        gen.grid, width, height
    )
    print(f"\nall cells visited: {all_visited}")
    print(f"edges: {edges}/{expected_edges} "
          "(should match for a valid spanning tree)")
    print(f"wall coherence between neighbors: {coherent}")

    # Same seed run twice should give the exact same maze
    gen2 = MazeGenerator(width, height, seed=seed)
    gen2.generate_perfect()
    same = all(
        c1.walls == c2.walls
        for r1, r2 in zip(gen.grid, gen2.grid)
        for c1, c2 in zip(r1, r2)
    )
    print(f"same seed reproducible: {same}")


if __name__ == "__main__":
    main()
