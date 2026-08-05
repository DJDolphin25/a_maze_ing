# mazegen/hex_format.py
from typing import List, Tuple
from .cells import Cell


def serialize_maze(
    grid: List[List[Cell]],
    entry: Tuple[int, int],
    exit: Tuple[int, int],
    solution_path: str,
) -> str:
    """Writes the maze out in the exact format we need: one line of hex
    digits per row (each digit is a cell's walls), then a blank line,
    then entry, exit and the solution path, one per line.

    Args:
        grid: the maze, as a list of rows of Cell.
        entry: (x, y) coordinates of the starting cell.
        exit: (x, y) coordinates of the target cell.
        solution_path: the shortest path from entry to exit, as a
            string of 'N', 'E', 'S', 'W' moves.

    Returns:
        The full text to write to the output file, ending in '\\n'.
    """
    lines = []
    for row in grid:
        lines.append("".join(cell.to_hex() for cell in row))

    lines.append("")  # Blank line in between
    lines.append(f"{entry[0]},{entry[1]}")  # Entry coordinates, x,y
    lines.append(f"{exit[0]},{exit[1]}")  # Exit coordinates, x,y
    lines.append(solution_path)  # Path as a string of N/E/S/W
    return "\n".join(lines) + "\n"
