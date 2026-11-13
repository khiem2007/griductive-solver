from proofledger.cases.import_json import Definition
from proofledger.contracts.messages import PublicSnapshot
from proofledger.contracts.values import Clue, Verdict


class Vault:
    """Own private information; only published records leave this boundary."""

    def __init__(self, definition: Definition):
        """Store the complete private definition and publish only starting cells."""
        self._definition = definition
        self._published: set[str] = set(definition.initial)

    def reset(self):
        """Restore the set of published cells to the puzzle's initial reveals."""
        self._published = set(self._definition.initial)

    def reveal(self, cell: str, verdict: Verdict) -> Clue | None:
        """Publish a cell's clue only when a new verdict matches the private solution."""
        if cell in self._published or dict(self._definition.solution).get(cell) != verdict:
            return None
        clue = dict(self._definition.clues)[cell]
        self._published.add(cell)
        return clue

    def snapshot(self, session: str, revision: int) -> PublicSnapshot:
        """Create an immutable view containing only identities and published evidence."""
        return PublicSnapshot(
            session, revision, self._definition.identifier, self._definition.size,
            self._definition.people,
            tuple((cell, clue) for cell, clue in self._definition.clues if cell in self._published),
            tuple((cell, status) for cell, status in self._definition.solution
                  if cell in self._published),
        )
