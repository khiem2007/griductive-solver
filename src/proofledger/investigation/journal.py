from dataclasses import dataclass

from proofledger.contracts.values import Clue, Verdict
from proofledger.reasoning.inference import SatQuery


@dataclass(frozen=True)
class Entry:
    step: int
    active_clues: tuple[str, ...]
    sat_calls: int
    cell: str
    verdict: Verdict
    revealed_clue: str
    sat_queries: tuple[SatQuery, ...]
    revealed_statement: Clue
