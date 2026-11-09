from dataclasses import dataclass
from pathlib import Path

from proofledger.cases.import_json import Definition, PuzzleError, load_definition


@dataclass(frozen=True)
class CatalogEntry:
    path: Path
    definition: Definition | None = None
    error: str = ""


def sample_directory() -> Path:
    return Path(__file__).resolve().parents[1] / "samples"


def discover(directory: Path) -> tuple[CatalogEntry, ...]:
    entries = []
    for path in sorted(directory.glob("*.json")):
        try:
            entries.append(CatalogEntry(path, load_definition(path)))
        except PuzzleError as exc:
            entries.append(CatalogEntry(path, error=str(exc)))
    return tuple(entries)
