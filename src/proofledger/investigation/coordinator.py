from uuid import uuid4

from proofledger.cases.import_json import Definition
from proofledger.cases.vault import Vault
from proofledger.contracts.messages import PublicSnapshot
from proofledger.contracts.values import Clue, Outcome, Verdict
from proofledger.investigation.journal import Entry
from proofledger.reasoning.inference import Analysis, next_move


class Investigation:
    def __init__(self, definition: Definition):
        self.title = definition.title
        self.description = definition.description
        self.initial_count = len(definition.initial)
        self._vault = Vault(definition)
        self._session = uuid4().hex
        self._revision = 0
        self._journal: list[Entry] = []
        self.analysis: Analysis | None = None
        self.selected: str | None = None
        self.evidence_owner: str | None = None

    @property
    def public(self) -> PublicSnapshot:
        return self._vault.snapshot(self._session, self._revision)

    @property
    def journal(self) -> tuple[Entry, ...]:
        return tuple(self._journal)

    def receive(self, analysis: Analysis) -> bool:
        if (analysis.session, analysis.revision) != (self._session, self._revision):
            return False
        self.analysis = analysis
        return True

    def reset(self):
        self._vault.reset()
        self._revision += 1
        self._journal.clear()
        self.analysis = None
        self.selected = self.evidence_owner = None

    def hint(self) -> tuple[str, Verdict] | None:
        if self.analysis is None:
            return None
        return next_move(self.public, self.analysis)

    def select(self, cell: str, observe: bool = False) -> bool:
        snapshot = self.public
        if cell not in {person.cell for person in snapshot.people}:
            return False
        if observe and cell not in dict(snapshot.clues):
            return False
        self.selected = cell
        self.evidence_owner = cell if cell in dict(snapshot.clues) else None
        return True

    @property
    def evidence(self) -> Clue | None:
        return dict(self.public.clues).get(self.evidence_owner)

    @property
    def references(self) -> tuple[str, ...]:
        clue = self.evidence
        return clue.cells if clue else ()

    def submit(self, cell: str | None, verdict: Verdict) -> Outcome:
        snapshot = self.public
        if (cell not in {person.cell for person in snapshot.people}
                or cell in dict(snapshot.facts)
                or verdict not in (Verdict.CRIMINAL, Verdict.INNOCENT)):
            return Outcome.INVALID
        analysis = self.analysis
        if analysis is None or (analysis.session, analysis.revision) != (
                snapshot.session, snapshot.revision):
            return Outcome.PENDING
        if analysis.inconsistent:
            return Outcome.INCONSISTENT
        forced = dict(analysis.classifications).get(cell, Verdict.UNKNOWN)
        if forced == Verdict.UNKNOWN:
            return Outcome.NOT_PROVABLE
        if forced != verdict:
            return Outcome.CONTRADICTED
        clue = self._vault.reveal(cell, verdict)
        if clue is None:
            return Outcome.INCONSISTENT
        self._journal.append(Entry(len(self._journal) + 1,
                                   tuple(c.identifier for _, c in snapshot.clues),
                                   analysis.counters.sat_calls, cell, verdict, clue.identifier,
                                   analysis.queries, clue))
        self._revision += 1
        self.analysis = None
        self.selected = cell
        self.evidence_owner = cell
        return Outcome.ACCEPTED
