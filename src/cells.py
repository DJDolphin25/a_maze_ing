from enum import IntFlag

class Wall(IntFlag):
    NONE = 0
    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    ALL = 15

    @classmethod
    def opposite(cls, wall: "Wall") -> "Wall":
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
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.walls: Wall = Wall.ALL
        self.visited: bool = False

    def remove_wall(self, wall: Wall) -> None:
        self.walls &= ~wall

    def add_wall(self, wall: Wall) -> None:
        self.walls |= wall

    def has_wall(self, wall: Wall) -> bool:
        return bool(self.walls & wall)

    def to_hex(self) -> str:
        return f"{self.walls.value:X}"

    def __repr__(self) -> str:
        return f"Cell(x={self.x}, y={self.y}, walls={self.walls!r})"
