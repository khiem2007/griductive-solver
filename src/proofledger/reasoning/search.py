from collections import Counter
from dataclasses import dataclass, fields
from time import perf_counter

from proofledger.reasoning.compiler import Formula


@dataclass(frozen=True)
class Counters:
    sat_calls: int = 0
    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    pure_literals: int = 0
    runtime_ms: float = 0.0

    def __add__(self, other: "Counters") -> "Counters":
        return Counters(**{f.name: getattr(self, f.name) + getattr(other, f.name)
                           for f in fields(self)})


@dataclass(frozen=True)
class SearchResult:
    satisfiable: bool
    values: tuple[bool, ...]
    counters: Counters


def solve(formula: Formula, assumptions: tuple[int, ...] = (), pure: bool = True) -> SearchResult:
    """Recursive DPLL with propagation before each deterministic branch."""
    started = perf_counter()
    source = formula.clauses + tuple((value,) for value in assumptions)
    decisions = propagations = backtracks = pure_count = 0
    def visit(active, assigned):
        nonlocal decisions, propagations, backtracks, pure_count
        while True:
            remaining = []
            conflict = False
            for clause in active:
                if any(assigned.get(abs(lit)) == (lit > 0) for lit in clause
                       if abs(lit) in assigned):
                    continue
                unresolved = tuple(lit for lit in clause if abs(lit) not in assigned)
                if not unresolved:
                    conflict = True
                    break
                remaining.append(unresolved)
            if conflict:
                return None
            if not remaining:
                return assigned
            active = tuple(remaining)
            units = {clause[0] for clause in remaining if len(clause) == 1}
            if any(-unit in units for unit in units):
                return None
            if units:
                assigned.update((abs(unit), unit > 0) for unit in units)
                propagations += len(units)
                continue
            occurrences = Counter(lit for clause in remaining for lit in clause)
            singles = sorted((lit for lit in occurrences if -lit not in occurrences), key=abs)
            if pure and singles:
                assigned.update((abs(lit), lit > 0) for lit in singles)
                pure_count += len(singles)
                continue
            frequency = Counter()
            for lit, count in occurrences.items():
                frequency[abs(lit)] += count
            primary = [variable for variable in frequency if variable <= len(formula.cells)]
            pivot = min(primary or frequency, key=lambda variable: (-frequency[variable], variable))
            decisions += 1
            # Each recursive call owns a new assignment. Failed children cause
            # backtracking; a contradiction at the root is not a backtrack.
            for value in (True, False):
                model = visit(active, {**assigned, pivot: value})
                if model is not None:
                    return model
                backtracks += 1
            return None

    model = visit(source, {})
    counters = Counters(1, decisions, propagations, backtracks, pure_count,
                        (perf_counter() - started) * 1000)
    values = tuple(model.get(i, False) for i in range(1, formula.variables + 1)) if model is not None else ()
    return SearchResult(model is not None, values, counters)
