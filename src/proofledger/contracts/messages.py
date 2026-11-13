from dataclasses import dataclass

from proofledger.contracts.values import Clue, Person, Verdict


@dataclass(frozen=True)
class PublicSnapshot:
    session: str
    revision: int
    puzzle_id: str
    size: int
    people: tuple[Person, ...]
    clues: tuple[tuple[str, Clue], ...]
    facts: tuple[tuple[str, Verdict], ...]

    @property
    def solved(self) -> bool:
        """Report whether every identity already has a published verdict."""
        return len(self.facts) == len(self.people)
