import csv
import json
from pathlib import Path
from time import perf_counter

from core.game_engine import GameEngine
from core.models import PublicState
from core.puzzle_loader import load_puzzle
from game.session import GameSession
from logic.agent import LogicAgent
from logic.cnf_encoder import CNFEncoder


ROOT = Path(__file__).parent
OUTPUT = ROOT / "output"


def run_case(path, use_pure_literal=True):
    puzzle = load_puzzle(path)
    agent = LogicAgent(use_pure_literal)
    session = GameSession(GameEngine(puzzle), agent)
    cumulative = {
        "sat_calls": 0,
        "decisions": 0,
        "propagations": 0,
        "backtracks": 0,
        "pure_literals": 0,
    }
    started = perf_counter()
    while not session.engine.is_solved():
        cumulative["sat_calls"] += session.analysis.stats.sat_calls
        cumulative["decisions"] += session.analysis.stats.decisions
        cumulative["propagations"] += session.analysis.stats.propagations
        cumulative["backtracks"] += session.analysis.stats.backtracks
        cumulative["pure_literals"] += session.analysis.stats.pure_literals
        move = agent.next_forced(session.public, session.analysis)
        if move is None:
            break
        result, _ = session.submit(*move)
        if result.value != "ACCEPTED":
            break
    elapsed_ms = (perf_counter() - started) * 1000

    # The uniqueness query receives every clue but never receives hidden labels.
    full_public = PublicState(
        puzzle_id=puzzle.puzzle_id,
        size=puzzle.size,
        characters=dict(puzzle.characters),
        revealed_clues=dict(puzzle.clues),
    )
    encoder = CNFEncoder(puzzle.characters)
    full_clauses = encoder.encode_public_state(full_public)
    return {
        "puzzle": puzzle.puzzle_id,
        "size": f"{puzzle.size}x{puzzle.size}",
        "primary_variables": encoder.primary_variables,
        "auxiliary_variables": encoder.auxiliary_variables,
        "full_clauses": len(full_clauses),
        **cumulative,
        "deduction_steps": len(session.trace),
        "solved": session.engine.is_solved(),
        "uniqueness": agent.uniqueness_check(full_public),
        "runtime_ms": round(elapsed_ms, 3),
        "trace": [
            {
                "step": entry.step,
                "active_clues": entry.active_clues,
                "sat_calls": entry.sat_calls,
                "cell": entry.cell,
                "verdict": entry.verdict.value,
                "revealed_clue": entry.revealed_clue,
            }
            for entry in session.trace
        ],
    }


def main():
    OUTPUT.mkdir(exist_ok=True)
    results = [run_case(path) for path in sorted((ROOT / "puzzles").glob("*.json"))]
    columns = [
        "puzzle", "size", "primary_variables", "auxiliary_variables",
        "full_clauses", "sat_calls", "decisions", "propagations",
        "backtracks", "pure_literals", "deduction_steps", "solved",
        "uniqueness", "runtime_ms",
    ]
    with (OUTPUT / "experiments.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows({key: row[key] for key in columns} for row in results)
    with (OUTPUT / "deduction_traces.json").open("w", encoding="utf-8") as stream:
        json.dump(
            {row["puzzle"]: row["trace"] for row in results},
            stream,
            indent=2,
        )
    for row in results:
        print(
            f"{row['puzzle']}: solved={row['solved']}, "
            f"unique={row['uniqueness']}, steps={row['deduction_steps']}, "
            f"runtime={row['runtime_ms']:.3f} ms"
        )

    write_ablation()


def write_ablation():
    """Same puzzle set, solver with and without pure-literal elimination."""
    paths = sorted((ROOT / "puzzles").glob("*.json"))
    columns = [
        "puzzle", "decisions_off", "decisions_on", "propagations_off",
        "propagations_on", "backtracks_off", "backtracks_on",
        "pure_literals_on", "runtime_ms_off", "runtime_ms_on",
    ]
    rows = []
    for path in paths:
        off = run_case(path, use_pure_literal=False)
        on = run_case(path, use_pure_literal=True)
        rows.append({
            "puzzle": off["puzzle"],
            "decisions_off": off["decisions"], "decisions_on": on["decisions"],
            "propagations_off": off["propagations"],
            "propagations_on": on["propagations"],
            "backtracks_off": off["backtracks"], "backtracks_on": on["backtracks"],
            "pure_literals_on": on["pure_literals"],
            "runtime_ms_off": off["runtime_ms"], "runtime_ms_on": on["runtime_ms"],
        })
    with (OUTPUT / "pure_literal_ablation.csv").open(
        "w", newline="", encoding="utf-8"
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print("\npure-literal elimination (off -> on)")
    for row in rows:
        print(
            f"  {row['puzzle']}: decisions {row['decisions_off']} -> "
            f"{row['decisions_on']}, propagations {row['propagations_off']} -> "
            f"{row['propagations_on']}, pure literals {row['pure_literals_on']}"
        )


if __name__ == "__main__":
    main()

