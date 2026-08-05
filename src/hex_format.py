from typing import List
from .cells import Cell

def serialize_maze(grid: List[List[Cell]], solution_path: str) -> str:
    """Writes the maze out in the exact format we need: one line of hex
    digits per row (each digit is a cell's walls), then a blank line,
    then the solution path.
    """
    lines = []
    for row in grid:
        lines.append("".join(cell.to_hex() for cell in row))

    lines.append("")  # Blank line in between
    lines.append(solution_path)  # Path as a string of N/E/S/W
    return "\n".join(lines) + "\n"