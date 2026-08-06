# src/display.py
"""Interactive ASCII terminal display for a generated maze.

Separate from mazegen/ on purpose, same reasoning as config.py: this is
specific to a_maze_ing.py's terminal UI, not something a future project
reusing the mazegen package would need.
"""
from typing import FrozenSet, List, Optional, Tuple

from .mazegen import MazeGenerator, solve_bfs
from .mazegen.cells import Cell, Wall

# Cycled through with "Rotate the wall colours", using the 256-colour ANSI
# palette (\033[38;5;Nm) instead of the basic 8 colours, for more variety.
WALL_COLORS = [
    "\033[38;5;15m",   # White
    "\033[38;5;196m",  # Red
    "\033[38;5;208m",  # Orange
    "\033[38;5;226m",  # Yellow
    "\033[38;5;46m",   # Green
    "\033[38;5;51m",   # Cyan
    "\033[38;5;33m",   # Blue
    "\033[38;5;129m",  # Purple
]
# Resets back to the terminal's default color after each colored piece.
RESET = "\033[0m"

# Entry/exit/path have their own fixed colour, independent of the wall
# colour rotation - only "wall colour" is meant to rotate, per the menu.
ENTRY_COLOR = "\033[1;32m"  # bold green
EXIT_COLOR = "\033[1;31m"   # bold red
PATH_COLOR = "\033[36m"     # cyan

# Each mark is 3 characters wide (color codes aside), to fit the same
# cell width as EMPTY_MARK and the horizontal wall segments.
ENTRY_MARK = f"{ENTRY_COLOR} S {RESET}"
EXIT_MARK = f"{EXIT_COLOR} X {RESET}"
PATH_MARK = f"{PATH_COLOR} · {RESET}"
EMPTY_MARK = "   "

# Cycled through with "Rotate the '42' pattern colour" - a separate
# rotation from WALL_COLORS, per the subject's optional suggestion to
# give the "42" pattern its own colour. Greys/white first, to match
# the subject's own reference screenshot.
PATTERN_COLORS = [
    "\033[38;5;250m",  # Light grey
    "\033[38;5;15m",   # White
    "\033[38;5;244m",  # Grey
    "\033[38;5;39m",   # Light blue
]
# Fills a "42" cell's interior solid, so the pattern reads as a shape
# instead of just more walls. 3 characters wide, same reason as above.
PATTERN_FILL = "███"

# Box-drawing character for every possible combination of lines meeting at
# a grid intersection, indexed by 4 bits: up<<3 | right<<2 | down<<1 | left.
# E.g. bits 0b0110 (right+down, no up/left) is a top-left corner: '┌'.
_JUNCTIONS = [
    " ", "╴", "╷", "┐",
    "╶", "─", "┌", "┬",
    "╵", "┘", "│", "┤",
    "└", "┴", "├", "┼",
]
# H_WALL is repeated 3x to draw a horizontal segment (cells are 3 chars
# wide); V_WALL is used once, since a vertical segment is 1 char wide.
H_WALL = "─"
V_WALL = "│"


def path_cells(entry: Tuple[int, int], path: str) -> List[Tuple[int, int]]:
    """Walks `path` from entry and returns every (x, y) cell it visits.

    Args:
        entry: (x, y) coordinates of the starting cell.
        path: the path as a string of 'N', 'E', 'S', 'W' moves.

    Returns:
        The ordered list of cells visited, entry included, one per step.
    """
    moves = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    x, y = entry
    cells = [(x, y)]
    for move in path:
        move_x, move_y = moves[move]
        x, y = x + move_x, y + move_y
        cells.append((x, y))
    return cells


def render_maze(
    grid: List[List[Cell]],
    entry: Tuple[int, int],
    exit: Tuple[int, int],
    path: Optional[str],
    color: str,
    pattern_color: str = "",
) -> str:
    """Builds the ASCII rendering of the maze, walls colored, with
    entry/exit marked and the solution path optionally overlaid.

    Args:
        grid: the maze, as a list of rows of Cell.
        entry: (x, y) coordinates of the entry cell.
        exit: (x, y) coordinates of the exit cell.
        path: the solution path as N/E/S/W moves, or None to hide it.
        color: ANSI color escape code to draw the walls with.
        pattern_color: ANSI color escape code for the "42" pattern
            cells' fill. Defaults to no color (terminal's default fg).

    Returns:
        The full ASCII rendering, ready to print.
    """
    height = len(grid)
    width = len(grid[0])
    on_path: FrozenSet[Tuple[int, int]] = (
        frozenset(path_cells(entry, path)) if path is not None else frozenset()
    )

    def closed_h(row: int, col: int) -> bool:
        """Is there a closed wall between row-1 and row, at column col?"""
        if row == 0:
            return grid[0][col].has_wall(Wall.NORTH)
        if row == height:
            return grid[height - 1][col].has_wall(Wall.SOUTH)
        return grid[row][col].has_wall(Wall.NORTH)

    def closed_v(col: int, row: int) -> bool:
        """Is there a closed wall between col-1 and col, at row row?"""
        if col == 0:
            return grid[row][0].has_wall(Wall.WEST)
        if col == width:
            return grid[row][width - 1].has_wall(Wall.EAST)
        return grid[row][col].has_wall(Wall.WEST)

    def junction(col: int, row: int) -> str:
        """Box-drawing character for the grid intersection at (col, row)."""
        up = row > 0 and closed_v(col, row - 1)
        down = row < height and closed_v(col, row)
        left = col > 0 and closed_h(row, col - 1)
        right = col < width and closed_h(row, col)
        # See _JUNCTIONS above for what each bit combination maps to.
        bits = (up << 3) | (right << 2) | (down << 1) | left
        return _JUNCTIONS[bits]

    def h_segment(row: int, col: int) -> str:
        """Colored '───' if closed, 3 blank spaces if open."""
        if not closed_h(row, col):
            return "   "
        return f"{color}{H_WALL * 3}{RESET}"

    def v_segment(col: int, row: int) -> str:
        """Colored '│' if closed, one blank space if open."""
        if not closed_v(col, row):
            return " "
        return f"{color}{V_WALL}{RESET}"

    # Each row of the maze needs 2 lines of text: one for the wall
    # crossings + horizontal segments above it, one for the vertical
    # segments + cell contents. The very last row only needs the top line.
    lines = []
    for row in range(height + 1):
        h_line = ""
        for col in range(width):
            h_line += f"{color}{junction(col, row)}{RESET}"
            h_line += h_segment(row, col)
        h_line += f"{color}{junction(width, row)}{RESET}"
        lines.append(h_line)

        if row < height:
            v_line = ""
            for col in range(width):
                v_line += v_segment(col, row)
                v_line += _cell_mark(
                    grid, (col, row), entry, exit, on_path, pattern_color
                )
            v_line += v_segment(width, row)
            lines.append(v_line)

    return "\n".join(lines)


def _cell_mark(
    grid: List[List[Cell]],
    cell: Tuple[int, int],
    entry: Tuple[int, int],
    exit: Tuple[int, int],
    on_path: FrozenSet[Tuple[int, int]],
    pattern_color: str,
) -> str:
    """What to print inside one cell: entry/exit marker, "42" fill,
    path dot, or blank."""
    if cell == entry:
        return ENTRY_MARK
    if cell == exit:
        return EXIT_MARK
    # A "42" pattern cell has every wall closed - that combination
    # never happens otherwise, since every normal cell keeps at least
    # one open wall to stay connected (see non_perfect.py).
    cell_x, cell_y = cell
    if grid[cell_y][cell_x].walls == Wall.ALL:
        return f"{pattern_color}{PATTERN_FILL}{RESET}"
    if cell in on_path:
        return PATH_MARK
    return EMPTY_MARK


def run_interactive(
    generator: MazeGenerator,
    path: str,
    width: int,
    height: int,
    entry: Tuple[int, int],
    exit: Tuple[int, int],
    perfect: bool,
) -> None:
    """Runs the "=== A-Maze-ing ===" menu loop until the user quits.

    The first maze shown is `generator`/`path`, exactly as already written
    to the output file - the caller builds it once and hands it over here,
    instead of this function generating its own. The two must match:
    the grading criteria explicitly checks that the first displayed maze
    is the same one saved to disk. Only "Re-generate" builds a new one,
    always with a fresh random seed, since that's the point of that option -
    but it still respects `perfect`, so a PERFECT=False maze doesn't
    suddenly turn into a perfect one after regenerating.

    Args:
        generator: the already-built MazeGenerator for the first maze
            shown (same one written to the output file).
        path: the already-solved shortest path for `generator`.
        width: maze width, in cells.
        height: maze height, in cells.
        entry: (x, y) coordinates of the entry cell.
        exit: (x, y) coordinates of the exit cell.
        perfect: which mode "Re-generate" should keep using.
    """
    def build(use_seed: Optional[int]) -> Tuple[MazeGenerator, str]:
        """Generates a fresh maze and solves it, ready to render."""
        gen = MazeGenerator(width, height, seed=use_seed)
        if perfect:
            gen.generate_perfect(entry[0], entry[1])
        else:
            gen.generate_non_perfect(entry[0], entry[1])
        path = solve_bfs(gen.grid, entry, exit)
        return gen, path

    gen = generator
    color_index = 0
    pattern_color_index = 0
    show_path = True

    while True:
        color = WALL_COLORS[color_index]
        pattern_color = PATTERN_COLORS[pattern_color_index]
        shown_path = path if show_path else None
        rendered = render_maze(
            gen.grid, entry, exit, shown_path, color, pattern_color
        )
        print(rendered)
        print()
        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show / Hide the shortest path")
        print("3. Rotate the wall colours")
        print("4. Rotate the '42' pattern colour")
        print("5. Quit")
        choice = input("Choice? (1-5): ").strip()

        if choice == "1":
            gen, path = build(None)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index = (color_index + 1) % len(WALL_COLORS)
        elif choice == "4":
            pattern_color_index = (
                (pattern_color_index + 1) % len(PATTERN_COLORS)
            )
        elif choice == "5":
            break
        else:
            print("Please choose 1, 2, 3, 4 or 5.")
