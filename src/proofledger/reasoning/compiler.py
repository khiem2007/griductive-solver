from dataclasses import dataclass
from itertools import product

from proofledger.contracts.messages import PublicSnapshot
from proofledger.contracts.values import Clue, Verdict


@dataclass(frozen=True)
class Formula:
    cells: tuple[str, ...]
    clauses: tuple[tuple[int, ...], ...]
    variables: int

    @property
    def auxiliary_variables(self) -> int:
        return self.variables - len(self.cells)


class Circuit:
    """Tseitin gates and a threshold-counting circuit, with constant folding."""

    def __init__(self, cells: tuple[str, ...]):
        self.cells = cells
        self.index = {cell: i + 1 for i, cell in enumerate(cells)}
        self.variables = len(cells)
        self.clauses: list[tuple[int, ...]] = []

    def require(self, value: int | bool):
        if type(value) is bool:
            if not value:
                self.clauses.append(())
        else:
            self.clauses.append((value,))

    def gate(self, kind: str, left: int | bool, right: int | bool) -> int | bool:
        if type(left) is bool or type(right) is bool:
            constant, other = (left, right) if type(left) is bool else (right, left)
            if kind == "AND":
                return other if constant else False
            if kind == "OR":
                return True if constant else other
            return self.negate(other) if constant else other
        self.variables += 1
        output = self.variables
        for a, b in product((False, True), repeat=2):
            wanted = (a and b) if kind == "AND" else (a or b) if kind == "OR" else a != b
            # A clause rules out exactly the wrong output for this input pair.
            self.clauses.append((-left if a else left, -right if b else right,
                                 output if wanted else -output))
        return output

    @staticmethod
    def negate(value: int | bool) -> int | bool:
        return not value if type(value) is bool else -value

    def statement(self, clue: Clue):
        inputs = tuple(self.index[cell] for cell in clue.cells)
        if clue.kind == "FACT":
            self.require(inputs[0] if clue.target == Verdict.CRIMINAL else -inputs[0])
        elif clue.kind in {"SAME", "DIFFERENT"}:
            different = self.gate("XOR", inputs[0], inputs[1])
            self.require(different if clue.kind == "DIFFERENT" else self.negate(different))
        elif clue.kind == "IMPLIES":
            self.clauses.append((-inputs[0], inputs[1]))
        elif clue.kind == "PARITY":
            parity: int | bool = False
            for value in inputs:
                parity = self.gate("XOR", parity, value)
            self.require(parity if clue.odd else self.negate(parity))
        else:
            if clue.kind not in {"EXACTLY", "AT_LEAST", "AT_MOST"}:
                raise ValueError(f"Cannot compile {clue.kind}")
            k = clue.count
            if clue.kind in {"AT_LEAST", "EXACTLY"}:
                self.bound(tuple(-value for value in inputs), len(inputs) - k)
            if clue.kind in {"AT_MOST", "EXACTLY"}:
                self.bound(inputs, k)

    def bound(self, inputs: tuple[int, ...], maximum: int):
        """Prefix lower bounds plus overflow clauses enforce an upper count limit.

        A true input starts/extends a count. A count persists into the next prefix.
        Reaching the limit forbids another true input. Reverse implications are
        unnecessary: auxiliary completions exist exactly for legal primary counts.
        """
        if maximum >= len(inputs):
            return
        if maximum == 0:
            self.clauses.extend((-value,) for value in inputs)
            return
        previous: dict[int, int] = {}
        for index, value in enumerate(inputs):
            if maximum in previous:
                self.clauses.append((-value, -previous[maximum]))
            if index == len(inputs) - 1:
                break
            current = {}
            for count in range(1, min(index + 1, maximum) + 1):
                self.variables += 1
                current[count] = self.variables
                if count == 1:
                    self.clauses.append((-value, current[count]))
                else:
                    self.clauses.append((-value, -previous[count - 1], current[count]))
                if count in previous:
                    self.clauses.append((-previous[count], current[count]))
            previous = current

    def finish(self) -> Formula:
        return Formula(self.cells, tuple(self.clauses), self.variables)


def compile_snapshot(snapshot: PublicSnapshot) -> Formula:
    circuit = Circuit(tuple(person.cell for person in snapshot.people))
    for _, clue in snapshot.clues:
        circuit.statement(clue)
    for cell, verdict in snapshot.facts:
        circuit.require(circuit.index[cell] if verdict == Verdict.CRIMINAL else -circuit.index[cell])
    return circuit.finish()
