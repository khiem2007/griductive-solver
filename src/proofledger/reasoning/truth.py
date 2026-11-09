from collections.abc import Mapping

from proofledger.contracts.values import Clue, Verdict


def holds(clue: Clue, assignment: Mapping[str, Verdict]) -> bool:
    """Interpret the statement directly, independently of any SAT representation."""
    values = tuple(assignment[cell] == Verdict.CRIMINAL for cell in clue.cells)
    match clue.kind:
        case "FACT":
            return assignment[clue.cells[0]] == clue.target
        case "SAME":
            return values[0] == values[1]
        case "DIFFERENT":
            return values[0] != values[1]
        case "IMPLIES":
            return not values[0] or values[1]
        case "EXACTLY":
            return sum(values) == clue.count
        case "AT_LEAST":
            return sum(values) >= clue.count
        case "AT_MOST":
            return sum(values) <= clue.count
        case "PARITY":
            return bool(sum(values) % 2) == clue.odd
        case _:
            raise ValueError(f"Unknown statement: {clue.kind}")
