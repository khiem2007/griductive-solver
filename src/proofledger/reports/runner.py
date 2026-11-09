import json
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter

from proofledger.cases.import_json import Definition, load_definition
from proofledger.contracts.messages import PublicSnapshot
from proofledger.contracts.values import Outcome
from proofledger.investigation.coordinator import Investigation
from proofledger.reasoning.compiler import compile_snapshot
from proofledger.reasoning.inference import analyze, uniqueness
from proofledger.reasoning.search import Counters


@dataclass(frozen=True)
class Report:
    metrics: dict
    trace: tuple[dict, ...]


def run_definition(definition: Definition, pure: bool = True) -> Report:
    started = perf_counter()
    case = Investigation(definition)
    cumulative = Counters()
    while not case.public.solved:
        analysis = analyze(case.public, pure)
        case.receive(analysis)
        cumulative += analysis.counters
        move = case.hint()
        if move is None:
            break
        if case.submit(*move) != Outcome.ACCEPTED:
            raise RuntimeError("A proved verdict was refused by the private reveal authority")
    elapsed = (perf_counter() - started) * 1000
    all_evidence = PublicSnapshot("batch-all", 0, definition.identifier, definition.size,
                                  definition.people, definition.clues, ())
    formula = compile_snapshot(all_evidence)
    counters = asdict(cumulative)
    counters.pop("runtime_ms")
    metrics = {
        "puzzle": definition.identifier,
        "size": f"{definition.size}x{definition.size}",
        "primary_variables": len(formula.cells),
        "auxiliary_variables": formula.auxiliary_variables,
        "full_clauses": len(formula.clauses),
        **counters,
        "deduction_steps": len(case.journal),
        "solved": case.public.solved,
        "uniqueness": uniqueness(formula, pure),
        "runtime_ms": round(elapsed, 3),
        "status": "SOLVED" if case.public.solved else "STALLED",
        "error": "" if case.public.solved else "No forced verdict remains in the public knowledge base",
        "source_file": "",
    }
    trace = tuple(json.loads(json.dumps(asdict(entry))) for entry in case.journal)
    return Report(metrics, trace)


def run_case(path: Path, pure: bool = True) -> Report:
    return run_definition(load_definition(path), pure)
