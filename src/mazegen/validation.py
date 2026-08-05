# mazegen/validation.py
from typing import Tuple


def validate_entry_exit(
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit: Tuple[int, int],
) -> None:
    """Makes sure entry and exit are usable coordinates for this maze.

    Per the subject: entry and exit must exist inside the maze bounds,
    be different from each other, and sit on the outer border of the
    maze, like the door of a real maze. This is just about their
    position - it doesn't open a hole in the outer wall. maze_analyzer.py
    never even looks at outward-facing walls (there's no "outside" cell
    to compare against), so the border stays fully closed everywhere,
    entry/exit included, exactly like generate_perfect() already builds it.

    Args:
        width: maze width, in cells.
        height: maze height, in cells.
        entry: (x, y) coordinates of the entry cell.
        exit: (x, y) coordinates of the exit cell.

    Raises:
        ValueError: if entry/exit are out of bounds, identical, or not
            on the outer border of the maze.
    """
    for name, (x, y) in (("entry", entry), ("exit", exit)):
        if not (0 <= x < width and 0 <= y < height):
            raise ValueError(
                f"{name} {(x, y)} is outside the maze bounds "
                f"({width}x{height})."
            )

    if entry == exit:
        raise ValueError(
            f"entry and exit must be different, both are {entry}."
        )

    for name, (x, y) in (("entry", entry), ("exit", exit)):
        # Border cell = leftmost/rightmost column or topmost/bottommost row
        on_border = x == 0 or x == width - 1 or y == 0 or y == height - 1
        if not on_border:
            raise ValueError(
                f"{name} {(x, y)} must be on the outer border of the maze."
            )
