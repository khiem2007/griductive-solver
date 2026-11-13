from dataclasses import dataclass
from pathlib import Path

from proofledger.cases.import_json import Definition, PuzzleError, load_definition


@dataclass(frozen=True)
class CatalogEntry:
    path: Path
    definition: Definition | None = None
    error: str = ""


def sample_directory() -> Path:
    """Locate the package's bundled JSON investigations."""
    return Path(__file__).resolve().parent.parent / "samples"


def discover(directory: Path) -> tuple[CatalogEntry, ...]:
    """Load every JSON file while preserving invalid files as catalog error entries."""
    entries = []
    for path in sorted(directory.glob("*.json")):
        try:
            entries.append(CatalogEntry(path, load_definition(path)))
        except PuzzleError as exc:
            entries.append(CatalogEntry(path, error=str(exc)))
    return tuple(entries)
