import json
from dataclasses import dataclass
from pathlib import Path

from proofledger.contracts.messages import PublicSnapshot
from proofledger.contracts.values import Clue, Person, Verdict, board_cells, cell_position
from proofledger.reasoning.compiler import compile_snapshot
from proofledger.reasoning.inference import uniqueness
from proofledger.reasoning.regions import resolve_region
from proofledger.reasoning.truth import holds


class PuzzleError(ValueError):
    """A file is unsuitable as a complete, truthful investigation."""


@dataclass(frozen=True)
class Definition:
    identifier: str
    title: str
    description: str
    size: int
    people: tuple[Person, ...]
    solution: tuple[tuple[str, Verdict], ...]
    clues: tuple[tuple[str, Clue], ...]
    initial: tuple[str, ...]


def _text(value, field: str, allow_empty: bool = False) -> str:
    """Validate a textual JSON field and return it unchanged."""
    if not isinstance(value, str) or (not value.strip() and not allow_empty):
        raise ValueError(f"{field} must be text" + ("" if allow_empty else " and nonempty"))
    return value


def _binary(value) -> Verdict:
    """Convert a value to a non-UNKNOWN verdict used by solutions and FACT clues."""
    verdict = Verdict(value)
    if verdict == Verdict.UNKNOWN:
        raise ValueError("Solution and FACT statements require a binary status")
    return verdict


def parse_clue(raw: dict, owner: str, size: int) -> Clue:
    """Validate one structured clue and normalize its referenced coordinates."""
    kind = _text(raw["type"], "Clue type").upper()
    identifier = _text(raw.get("id", f"evidence:{owner}"), "Clue ID")
    text = _text(raw.get("text", ""), "Clue text", allow_empty=True)
    data = raw.get("data", {})
    if not isinstance(data, dict):
        raise ValueError("Clue data must be an object")
    target, count, odd = None, None, False
    if kind == "FACT":
        cells = (data["cell"],)
        target = _binary(data["status"])
    elif kind in {"SAME", "DIFFERENT", "IMPLIES"}:
        cells = (data["a"], data["b"])
        if cells[0] == cells[1]:
            raise ValueError("A relation needs distinct endpoints")
    elif kind in {"EXACTLY", "AT_LEAST", "AT_MOST", "PARITY"}:
        cells = resolve_region(data["region"], size)
        if kind == "PARITY":
            parity = str(data["parity"]).upper()
            if parity not in {"EVEN", "ODD"}:
                raise ValueError("Parity must be EVEN or ODD")
            odd = parity == "ODD"
        else:
            count = data["k"]
            if type(count) is not int or not 0 <= count <= len(cells):
                raise ValueError("Count must be an integer within the region's bounds")
    else:
        raise ValueError(f"Unsupported clue type: {kind}")
    for cell in cells:
        cell_position(cell, size)
    return Clue(identifier, kind, cells, text, target, count, odd)


def parse_definition(raw: dict, *, require_unique: bool = True) -> Definition:
    """Validate a puzzle object and build an immutable private definition."""
    try:
        if not isinstance(raw, dict):
            raise ValueError("Puzzle root must be an object")
        size = raw["size"]
        if type(size) is not int or size not in (3, 4, 5):
            raise ValueError("Supported board sizes are integer 3, 4 and 5")
        cells = board_cells(size)
        people = tuple(Person(_text(p["cell"], "Cell"), _text(p["name"], "Name"),
                              _text(p["profession"], "Profession")) for p in raw["characters"])
        if len(people) != len(cells) or {p.cell for p in people} != set(cells):
            raise ValueError("Characters must cover each coordinate exactly once")
        people = tuple(sorted(people, key=lambda p: cells.index(p.cell)))
        names = [person.name.casefold() for person in people]
        if names != sorted(names):
            raise ValueError("Display names must be alphabetically ordered across row-major cells")
        if set(raw["solution"]) != set(cells) or set(raw["clues"]) != set(cells):
            raise ValueError("Solution and clue owners must each cover the full board")
        solution = tuple((c, _binary(raw["solution"][c])) for c in cells)
        clues = tuple((c, parse_clue(raw["clues"][c], c, size)) for c in cells)
        if len({clue.identifier for _, clue in clues}) != len(cells):
            raise ValueError("Clue IDs must be unique")
        for owner, clue in clues:
            if not holds(clue, dict(solution)):
                raise ValueError(f"Statement at {owner} disagrees with the solution")
        if not isinstance(raw["initially_revealed"], list):
            raise ValueError("Starting reveals must be a list")
        initial = tuple(_text(c, "Starting coordinate").upper()
                        for c in raw["initially_revealed"])
        if len(set(initial)) != len(initial) or not set(initial) <= set(cells):
            raise ValueError("Starting coordinates must be valid and unique")
        definition = Definition(_text(raw["id"], "ID"), _text(raw["title"], "Title"),
                                _text(raw.get("description", ""), "Description", True),
                                size, people, solution, clues, initial)
        if require_unique:
            all_clues = PublicSnapshot("validation", 0, definition.identifier, size, people, clues, ())
            if uniqueness(compile_snapshot(all_clues)) != "UNIQUE":
                raise ValueError("The complete clue set must determine exactly one board assignment")
        return definition
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise PuzzleError(f"Invalid puzzle: {exc}") from exc


def _unique_object(pairs):
    """Build a decoded JSON object while rejecting duplicate keys."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Repeated JSON key: {key}")
        result[key] = value
    return result


def load_definition(path: str | Path, *, require_unique: bool = True) -> Definition:
    """Read a UTF-8 puzzle file and validate it as a complete definition."""
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
        return parse_definition(raw, require_unique=require_unique)
    except (OSError, UnicodeError, ValueError) as exc:
        raise PuzzleError(f"{Path(path).name}: {exc}") from exc
