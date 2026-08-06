# mazegen/non_perfect.py
"""Turns an already-perfect maze into a Pac-Man-style playable board.

This is the PERFECT=False mode: start from the perfect spanning tree
generate_perfect() builds, then post-process it - carve the "42"
pattern, add loops (independent routes), and keep dead-ends rare -
without ever opening a 3x3 (or larger) fully-open area.
"""
import random
from typing import List, Set, Tuple

from .cells import Cell, Wall

Coord = Tuple[int, int]

# A small pixel-style "42": digit 4, a 1-cell gap, digit 2. 7 cells
# wide, 5 cells tall. '#' cells get fully closed off (Wall.ALL); '.'
# cells stay normal corridors.
PATTERN_42 = (
    "#.#.###",
    "#.#...#",
    "###.###",
    "..#.#..",
    "..#.###",
)


def make_playable(
    grid: List[List[Cell]],
    width: int,
    height: int,
    rng: random.Random,
    min_loops: int = 2,
    max_dead_ends: int = 2,
) -> None:
    """Post-processes a perfect grid into a playable board, in place.

    Args:
        grid: an already-perfect maze (see MazeGenerator.generate_perfect).
        width: maze width, in cells.
        height: maze height, in cells.
        rng: the generator's own random.Random, for reproducibility.
        min_loops: independent routes required (default matches
            maze_analyzer.py's --min-loops).
        max_dead_ends: real dead-ends tolerated (default matches
            maze_analyzer.py's --max-dead-ends).
    """
    corners, centre = _corners_and_centre(width, height)
    blocked = _place_pattern_42(grid, width, height, corners | centre)

    # Closing the "42" cells can split the tree generate_perfect() built;
    # reconnect everything else before touching anything else.
    _ensure_connected(grid, width, height, blocked)

    _add_loops(grid, width, height, rng, min_loops, blocked)
    _reduce_dead_ends(grid, width, height, rng, max_dead_ends, blocked)


def _neighbors(
    x: int, y: int, width: int, height: int
) -> List[Tuple[int, int, Wall]]:
    """The grid-adjacent (x, y) neighbors of a cell, with the shared wall."""
    result = []
    for move_x, move_y, wall in (
        (0, -1, Wall.NORTH),
        (1, 0, Wall.EAST),
        (0, 1, Wall.SOUTH),
        (-1, 0, Wall.WEST),
    ):
        neighbor_x, neighbor_y = x + move_x, y + move_y
        if 0 <= neighbor_x < width and 0 <= neighbor_y < height:
            result.append((neighbor_x, neighbor_y, wall))
    return result


def _corners_and_centre(
    width: int, height: int
) -> Tuple[Set[Coord], Set[Coord]]:
    """The 4 corners and the centre cell(s) - these must stay open."""
    corners = {
        (0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1),
    }
    col_mid = {width // 2} if width % 2 else {width // 2 - 1, width // 2}
    row_mid = {height // 2} if height % 2 else {height // 2 - 1, height // 2}
    centre = {(c, r) for r in row_mid for c in col_mid}
    return corners, centre


def _place_pattern_42(
    grid: List[List[Cell]], width: int, height: int, must_stay_open: Set[Coord]
) -> Set[Coord]:
    """Closes the cells that draw the "42" pattern, centered in the grid.

    Returns the set of cells closed. If the grid is too small to fit
    the pattern with a 1-cell margin from the border, prints a message
    and returns an empty set, per the subject's explicit allowance.
    """
    pattern_h = len(PATTERN_42)
    pattern_w = len(PATTERN_42[0])
    margin = 1
    if width < pattern_w + 2 * margin or height < pattern_h + 2 * margin:
        print(
            f"Warning: {width}x{height} maze is too small for the '42' "
            f"pattern (needs at least "
            f"{pattern_w + 2 * margin}x{pattern_h + 2 * margin}); "
            "skipping it."
        )
        return set()

    origin_x = (width - pattern_w) // 2
    origin_y = (height - pattern_h) // 2

    blocked: Set[Coord] = set()
    for row_index, row in enumerate(PATTERN_42):
        for col_index, char in enumerate(row):
            if char != "#":
                continue
            cell = (origin_x + col_index, origin_y + row_index)
            if cell in must_stay_open:
                continue
            blocked.add(cell)

    for x, y in blocked:
        grid[y][x].add_wall(Wall.ALL)
        # Coherence: a neighbor cell right outside the pattern must also
        # show this shared wall as closed, or the two would disagree
        # about whether there's a wall between them (see cells.py).
        for neighbor_x, neighbor_y, wall in _neighbors(x, y, width, height):
            if (neighbor_x, neighbor_y) not in blocked:
                grid[neighbor_y][neighbor_x].add_wall(Wall.opposite(wall))

    return blocked


def _region(
    grid: List[List[Cell]],
    width: int,
    height: int,
    start: Coord,
    blocked: Set[Coord],
) -> Set[Coord]:
    """Cells reachable from start through open walls, ignoring blocked ones."""
    seen = {start}
    stack = [start]
    while stack:
        current_x, current_y = stack.pop()
        current_cell = grid[current_y][current_x]
        for neighbor_x, neighbor_y, wall in _neighbors(
            current_x, current_y, width, height
        ):
            if (neighbor_x, neighbor_y) in blocked:
                continue
            if (neighbor_x, neighbor_y) in seen:
                continue
            if not current_cell.has_wall(wall):
                seen.add((neighbor_x, neighbor_y))
                stack.append((neighbor_x, neighbor_y))
    return seen


def _ensure_connected(
    grid: List[List[Cell]], width: int, height: int, blocked: Set[Coord]
) -> None:
    """Opens the minimum walls needed so every non-blocked cell connects.

    Carving the "42" pattern can split generate_perfect()'s tree into
    several pieces (whenever a closed cell used to be a junction, not
    a dead branch). This merges them back, one bridge wall at a time.
    """
    cells = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in blocked
    ]
    if not cells:
        return

    region = _region(grid, width, height, cells[0], blocked)
    remaining = set(cells) - region

    while remaining:
        # Look for any cell already in the connected region that sits
        # right next to a still-disconnected cell, and open that one
        # wall between them - a "bridge" merging the two pieces.
        bridge = None
        for region_x, region_y in region:
            for neighbor_x, neighbor_y, wall in _neighbors(
                region_x, region_y, width, height
            ):
                if (neighbor_x, neighbor_y) in remaining:
                    bridge = (region_x, region_y, neighbor_x, neighbor_y, wall)
                    break
            if bridge:
                break

        if bridge is None:
            break  # grid is contiguous, so this shouldn't happen

        region_x, region_y, remaining_x, remaining_y, wall = bridge
        grid[region_y][region_x].remove_wall(wall)
        grid[remaining_y][remaining_x].remove_wall(Wall.opposite(wall))

        region = _region(grid, width, height, cells[0], blocked)
        remaining = set(cells) - region


def _add_loops(
    grid: List[List[Cell]],
    width: int,
    height: int,
    rng: random.Random,
    min_loops: int,
    blocked: Set[Coord],
) -> None:
    """Opens extra walls to create independent routes.

    After _ensure_connected, the non-blocked cells form a spanning
    tree (zero loops). Every extra wall opened between two cells
    already in that tree creates exactly one independent loop -
    never a new connection, since everything is already reachable.
    """
    # Every wall between two grid-adjacent, non-blocked cells is a
    # candidate loop: (cell coords, neighbor coords, the wall between
    # them on each side).
    candidates = []
    for y in range(height):
        for x in range(width):
            if (x, y) in blocked:
                continue
            if x + 1 < width and (x + 1, y) not in blocked:
                candidates.append((x, y, x + 1, y, Wall.EAST, Wall.WEST))
            if y + 1 < height and (x, y + 1) not in blocked:
                candidates.append((x, y, x, y + 1, Wall.SOUTH, Wall.NORTH))
    rng.shuffle(candidates)

    loops = 0
    for cell_x, cell_y, other_x, other_y, wall, opposite_wall in candidates:
        if loops >= min_loops:
            break
        cell = grid[cell_y][cell_x]
        if not cell.has_wall(wall):
            continue  # already open, wouldn't add a loop
        big_area = _would_open_big_area(
            grid, width, height, cell_x, cell_y, other_x, other_y
        )
        if big_area:
            continue
        cell.remove_wall(wall)
        grid[other_y][other_x].remove_wall(opposite_wall)
        loops += 1


def _reduce_dead_ends(
    grid: List[List[Cell]],
    width: int,
    height: int,
    rng: random.Random,
    max_dead_ends: int,
    blocked: Set[Coord],
    max_attempts: int = 500,
) -> None:
    """Opens one more wall at real dead-ends until few enough remain."""
    for _ in range(max_attempts):
        dead_ends = _real_dead_ends(grid, width, height, blocked)
        if len(dead_ends) <= max_dead_ends:
            return

        rng.shuffle(dead_ends)
        dead_end_x, dead_end_y = dead_ends[0]
        cell = grid[dead_end_y][dead_end_x]
        openable = [
            (neighbor_x, neighbor_y, wall)
            for neighbor_x, neighbor_y, wall in _neighbors(
                dead_end_x, dead_end_y, width, height
            )
            if (neighbor_x, neighbor_y) not in blocked and cell.has_wall(wall)
        ]
        if not openable:
            continue
        rng.shuffle(openable)

        # Prefer an option that doesn't open a 3x3 area; if none of them
        # qualify, still open one anyway - clearing the dead-end wins.
        chosen = None
        for neighbor_x, neighbor_y, wall in openable:
            big_area = _would_open_big_area(
                grid, width, height, dead_end_x, dead_end_y,
                neighbor_x, neighbor_y,
            )
            if not big_area:
                chosen = (neighbor_x, neighbor_y, wall)
                break
        if chosen is None:
            chosen = openable[0]

        neighbor_x, neighbor_y, wall = chosen
        cell.remove_wall(wall)
        grid[neighbor_y][neighbor_x].remove_wall(Wall.opposite(wall))


def _real_dead_ends(
    grid: List[List[Cell]], width: int, height: int, blocked: Set[Coord]
) -> List[Coord]:
    """Cells with exactly 1 open passage that could still open another.

    Matches maze_analyzer.py's definition: a dead-end is only "real"
    if at least one of its closed walls faces a normal (non-blocked)
    neighbor - one enclosed only by "42" cells or the border doesn't
    count, since there's nothing to open there anyway.
    """
    dead_ends = []
    for y in range(height):
        for x in range(width):
            if (x, y) in blocked:
                continue
            cell = grid[y][x]
            neighbors = _neighbors(x, y, width, height)
            open_count = sum(
                1
                for neighbor_x, neighbor_y, wall in neighbors
                if (neighbor_x, neighbor_y) not in blocked
                and not cell.has_wall(wall)
            )
            if open_count != 1:
                continue
            has_openable_wall = any(
                (neighbor_x, neighbor_y) not in blocked and cell.has_wall(wall)
                for neighbor_x, neighbor_y, wall in neighbors
            )
            if has_openable_wall:
                dead_ends.append((x, y))
    return dead_ends


def _would_open_big_area(
    grid: List[List[Cell]],
    width: int,
    height: int,
    cell_x: int,
    cell_y: int,
    other_x: int,
    other_y: int,
) -> bool:
    """True if opening the wall between (cell_x,cell_y) and (other_x,other_y)
    would complete a fully-open 3x3 block of cells (never allowed, per
    the subject - a 2x2 or 2x3 open area is fine, 3x3 never is).
    """
    if width < 3 or height < 3:
        return False

    def is_open_between(
        from_x: int, from_y: int, to_x: int, to_y: int, side: Wall
    ) -> bool:
        """Same as has_wall(), but treats the not-yet-opened wall
        between cell_x,cell_y and other_x,other_y as already open."""
        if (from_x, from_y) == (cell_x, cell_y) and (to_x, to_y) == (
            other_x, other_y,
        ):
            return True
        return not grid[from_y][from_x].has_wall(side)

    def window_fully_open(window_x: int, window_y: int) -> bool:
        """Are all 12 internal connections of the 3x3 block whose
        top-left cell is (window_x, window_y) open? A 3x3 block has
        2 horizontal neighbor-pairs per row (3 rows) and 2 vertical
        neighbor-pairs per column (3 columns) - 12 shared walls total.
        """
        for row in range(window_y, window_y + 3):
            for col in range(window_x, window_x + 2):
                if not is_open_between(col, row, col + 1, row, Wall.EAST):
                    return False
        for col in range(window_x, window_x + 3):
            for row in range(window_y, window_y + 2):
                if not is_open_between(col, row, col, row + 1, Wall.SOUTH):
                    return False
        return True

    # A 3x3 window could be "completed" by this wall whether it's
    # anchored near cell_x,cell_y or near other_x,other_y, so we have
    # to try every window touching either cell, not just one of them.
    checked_windows = set()
    for center_x, center_y in ((cell_x, cell_y), (other_x, other_y)):
        x_range = range(max(0, center_x - 2), min(width - 3, center_x) + 1)
        y_range = range(max(0, center_y - 2), min(height - 3, center_y) + 1)
        for window_x in x_range:
            for window_y in y_range:
                if (window_x, window_y) in checked_windows:
                    continue
                checked_windows.add((window_x, window_y))
                if window_fully_open(window_x, window_y):
                    return True
    return False
