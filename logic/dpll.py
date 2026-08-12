from dataclasses import dataclass
from time import perf_counter


@dataclass
class DPLLStats:
    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    pure_literals: int = 0
    runtime_ms: float = 0.0


@dataclass
class SATResult:
    satisfiable: bool
    assignment: dict[int, bool]
    stats: DPLLStats


class DPLLSolver:
    """Small deterministic DPLL implementation used by every SAT query.

    Pure-literal elimination is optional so the report can compare the solver
    with and without it on the same puzzle set.
    """

    def __init__(self, use_pure_literal=True):
        self.use_pure_literal = use_pure_literal

    def solve(self, clauses, variable_count, assumptions=None):
        started = perf_counter()
        stats = DPLLStats()
        working = [tuple(clause) for clause in clauses]
        for literal in assumptions or []:
            working.append((literal,))
        assignment = self._dpll(working, {}, variable_count, stats)
        stats.runtime_ms = (perf_counter() - started) * 1000
        if assignment is None:
            return SATResult(False, {}, stats)
        for variable in range(1, variable_count + 1):
            assignment.setdefault(variable, False)
        return SATResult(True, assignment, stats)

    def _dpll(self, clauses, assignment, variable_count, stats):
        while True:
            reduced = self._simplify(clauses, assignment)
            if reduced is None:
                return None
            if not reduced:
                return assignment
            clauses = reduced

            units = sorted({clause[0] for clause in reduced if len(clause) == 1}, key=abs)
            if units:
                for literal in units:
                    variable, value = abs(literal), literal > 0
                    if variable in assignment and assignment[variable] != value:
                        return None
                    if variable not in assignment:
                        assignment[variable] = value
                        stats.propagations += 1
                continue

            if self.use_pure_literal:
                pure = self._pure_literals(reduced)
                if pure:
                    for literal in pure:
                        assignment[abs(literal)] = literal > 0
                    stats.pure_literals += len(pure)
                    continue

            break

        used = {abs(literal) for clause in clauses for literal in clause}
        variable = min(v for v in used if v not in assignment)
        stats.decisions += 1
        for value in (False, True):
            branch = dict(assignment)
            branch[variable] = value
            result = self._dpll(clauses, branch, variable_count, stats)
            if result is not None:
                return result
            stats.backtracks += 1
        return None

    @staticmethod
    def _pure_literals(clauses):
        """Variables that appear with a single polarity in the remaining clauses.

        Satisfying them can never lose a model, so they are assigned without a
        decision point.
        """
        positive, negative = set(), set()
        for clause in clauses:
            for literal in clause:
                (positive if literal > 0 else negative).add(abs(literal))
        pure = [v for v in positive - negative] + [-v for v in negative - positive]
        return sorted(pure, key=abs)

    @staticmethod
    def _simplify(clauses, assignment):
        result = []
        for clause in clauses:
            unresolved = []
            satisfied = False
            for literal in clause:
                variable = abs(literal)
                if variable not in assignment:
                    unresolved.append(literal)
                elif assignment[variable] == (literal > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unresolved:
                return None
            result.append(tuple(unresolved))
        return result

