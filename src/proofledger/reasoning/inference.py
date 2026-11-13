from dataclasses import dataclass

from proofledger.contracts.messages import PublicSnapshot
from proofledger.contracts.values import Verdict
from proofledger.reasoning.compiler import Formula, compile_snapshot
from proofledger.reasoning.search import Counters, SearchResult, solve


@dataclass(frozen=True)
class SatQuery:
    purpose: str
    cell: str | None
    assumptions: tuple[int, ...]
    result: str


@dataclass(frozen=True)
class Analysis:
    session: str
    revision: int
    classifications: tuple[tuple[str, Verdict], ...]
    inconsistent: bool
    uniqueness: str
    primary_variables: int
    auxiliary_variables: int
    clauses: int
    counters: Counters
    queries: tuple[SatQuery, ...] = ()


def uniqueness(formula: Formula, pure: bool = True, first: SearchResult | None = None) -> str:
    """Classify primary assignments as inconsistent, multiple, or unique."""
    first = first or solve(formula, pure=pure)
    if not first.satisfiable:
        return "INCONSISTENT"
    blocking = tuple(-i if first.values[i - 1] else i for i in range(1, len(formula.cells) + 1))
    alternative = Formula(formula.cells, formula.clauses + (blocking,), formula.variables)
    return "MULTIPLE" if solve(alternative, pure=pure).satisfiable else "UNIQUE"


def analyze(snapshot: PublicSnapshot, pure: bool = True) -> Analysis:
    """Classify every cell by SAT entailment using only a public snapshot."""
    formula = compile_snapshot(snapshot)
    baseline = solve(formula, pure=pure)
    counters = baseline.counters
    queries = [SatQuery("consistency", None, (), "SAT" if baseline.satisfiable else "UNSAT")]
    classifications = []
    if baseline.satisfiable:
        facts = dict(snapshot.facts)
        for variable, cell in enumerate(formula.cells, 1):
            if cell in facts:
                classifications.append((cell, facts[cell]))
                continue
            negative = solve(formula, (-variable,), pure)
            positive = solve(formula, (variable,), pure)
            queries.extend((
                SatQuery("assume_innocent", cell, (-variable,),
                         "SAT" if negative.satisfiable else "UNSAT"),
                SatQuery("assume_criminal", cell, (variable,),
                         "SAT" if positive.satisfiable else "UNSAT"),
            ))
            counters = counters + negative.counters + positive.counters
            verdict = Verdict.UNKNOWN
            if not negative.satisfiable:
                verdict = Verdict.CRIMINAL
            elif not positive.satisfiable:
                verdict = Verdict.INNOCENT
            classifications.append((cell, verdict))
    return Analysis(snapshot.session, snapshot.revision, tuple(classifications),
                    not baseline.satisfiable, uniqueness(formula, pure, baseline),
                    len(formula.cells), formula.auxiliary_variables, len(formula.clauses), counters,
                    tuple(queries))


def next_move(snapshot: PublicSnapshot, analysis: Analysis) -> tuple[str, Verdict] | None:
    """Choose the first unresolved forced verdict from a current analysis."""
    if analysis.session != snapshot.session or analysis.revision != snapshot.revision:
        return None
    known = dict(snapshot.facts)
    classified = dict(analysis.classifications)
    if not analysis.inconsistent:
        for person in snapshot.people:
            verdict = classified.get(person.cell, Verdict.UNKNOWN)
            if person.cell not in known and verdict != Verdict.UNKNOWN:
                return person.cell, verdict
    return None
