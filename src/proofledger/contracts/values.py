from dataclasses import dataclass
from enum import Enum


class Verdict(str, Enum):
    CRIMINAL = "CRIMINAL"
    INNOCENT = "INNOCENT"
    UNKNOWN = "UNKNOWN"


class Outcome(str, Enum):
    ACCEPTED = "ACCEPTED"
    NOT_PROVABLE = "NOT_PROVABLE"
    CONTRADICTED = "CONTRADICTED"
    INCONSISTENT = "INCONSISTENT"
    INVALID = "INVALID"
    PENDING = "PENDING"


@dataclass(frozen=True)
class Person:
    cell: str
    name: str
    profession: str


@dataclass(frozen=True)
class Clue:
    identifier: str
    kind: str
    cells: tuple[str, ...]
    text: str = ""
    target: Verdict | None = None
    count: int | None = None
    odd: bool = False


def board_cells(size: int) -> tuple[str, ...]:
    """Return every board coordinate in deterministic row-major order."""
    return tuple(f"{chr(65 + x)}{y}" for y in range(1, size + 1) for x in range(size))


def cell_position(cell: str, size: int) -> tuple[int, int]:
    """Validate a coordinate and convert it to zero-based row and column indexes."""
    if not isinstance(cell, str) or len(cell) < 2:
        raise ValueError("A coordinate needs a column letter and a row number")
    column, row = cell[0], cell[1:]
    if column not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or not row.isascii() or not row.isdigit():
        raise ValueError(f"Invalid coordinate: {cell}")
    if str(int(row)) != row or not 1 <= int(row) <= size or ord(column) - 65 >= size:
        raise ValueError(f"Coordinate outside this board: {cell}")
    return int(row) - 1, ord(column) - 65
