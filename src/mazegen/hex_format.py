# mazegen/hex_format.py
from typing import List
from .cells import Cell


def serialize_maze(grid: List[List[Cell]], solution_path: str) -> str:
    """Writes the maze out in the exact format we need: one line of hex
    digits per row (each digit is a cell's walls), then a blank line,
    then the solution path.

    Args:
        grid: the maze, as a list of rows of Cell.
        solution_path: the shortest path from entry to exit, as a
            string of 'N', 'E', 'S', 'W' moves.

    Returns:
        The full text to write to the output file, ending in '\\n'.
    """
    lines = []
    for row in grid:
        lines.append("".join(cell.to_hex() for cell in row))

    lines.append("")  # Blank line in between
    lines.append(solution_path)  # Path as a string of N/E/S/W
    return "\n".join(lines) + "\n"
