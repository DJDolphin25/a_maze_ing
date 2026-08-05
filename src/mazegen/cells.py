# mazegen/cells.py
from enum import IntFlag


class Wall(IntFlag):
    """One bit per cardinal direction, so a cell's 4 walls fit in a
    single number.

    NORTH/EAST/SOUTH/WEST are the bit positions the output format
    expects (bit0=North, bit1=East, bit2=South, bit3=West), so a
    cell's Wall value can be dumped straight to a hex digit with
    Cell.to_hex().
    """

    NONE = 0    # 0b0000
    NORTH = 1   # 0b0001
    EAST = 2    # 0b0010
    SOUTH = 4   # 0b0100
    WEST = 8    # 0b1000
    ALL = 15    # 0b1111

    @classmethod
    def opposite(cls, wall: "Wall") -> "Wall":
        """The wall a neighboring cell has on its side of 'wall'.

        Two cells share a wall, so when you open a wall on one cell
        you must also open the opposite wall on its neighbor -
        otherwise the two cells would disagree about whether there's
        a wall between them.

        Args:
            wall: a single direction (NORTH, EAST, SOUTH or WEST).

        Returns:
            The opposite direction, or NONE if 'wall' isn't one of
            the four cardinal directions.
        """
        if wall == cls.NORTH:
            return cls.SOUTH
        if wall == cls.SOUTH:
            return cls.NORTH
        if wall == cls.EAST:
            return cls.WEST
        if wall == cls.WEST:
            return cls.EAST
        return cls.NONE


class Cell:
    """A single cell of the maze grid.

    Attributes:
        x: column index in the grid.
        y: row index in the grid.
        walls: which of the 4 walls are still closed (starts fully
            closed, and generation opens walls as it connects cells).
        visited: whether the generator has already reached this cell.
    """

    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.walls: Wall = Wall.ALL
        self.visited: bool = False

    def remove_wall(self, wall: Wall) -> None:
        """Opens 'wall' on this cell (e.g. to connect it to a neighbor)."""
        self.walls &= ~wall

    def add_wall(self, wall: Wall) -> None:
        """Closes 'wall' on this cell."""
        self.walls |= wall

    def has_wall(self, wall: Wall) -> bool:
        """True if 'wall' is currently closed on this cell."""
        return bool(self.walls & wall)

    def to_hex(self) -> str:
        """This cell's walls as a single hex digit, per the output format."""
        return f"{self.walls.value:X}"

    def __repr__(self) -> str:
        """Debug string showing position and wall state."""
        return f"Cell(x={self.x}, y={self.y}, walls={self.walls!r})"
