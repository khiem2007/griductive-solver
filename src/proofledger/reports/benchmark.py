"""Bound each file/mode run without omitting invalid inputs or failed runs."""
import math
import multiprocessing as mp
from dataclasses import replace
from pathlib import Path
from time import perf_counter

from proofledger.cases.import_json import PuzzleError
from proofledger.reports.runner import Report, run_case


def failure(path: Path, status: str, error: str, runtime_ms: float) -> Report:
    metrics = {name: None for name in (
        "size", "primary_variables", "auxiliary_variables", "full_clauses", "sat_calls",
        "decisions", "propagations", "backtracks", "pure_literals", "deduction_steps")}
    metrics.update(puzzle=path.stem, source_file=path.name, solved=False, uniqueness="UNKNOWN",
                   runtime_ms=round(runtime_ms, 3), status=status, error=error)
    return Report(metrics, ())


def _run(sender, path: Path, pure: bool):
    started = perf_counter()
    try:
        report = run_case(path, pure)
        report = replace(report, metrics={**report.metrics, "source_file": path.name})
    except Exception as exc:
        report = failure(path, "INVALID" if isinstance(exc, PuzzleError) else "ERROR",
                         f"{type(exc).__name__}: {exc}", (perf_counter() - started) * 1000)
    try:
        sender.send(report)
    finally:
        sender.close()


def run_limited(path: Path, pure: bool, timeout: float) -> Report:
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout must be positive")
    context = mp.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=_run, args=(sender, path, pure), daemon=True)
    started = perf_counter()
    try:
        process.start()
        sender.close()
        if not receiver.poll(timeout):
            return failure(path, "TIMEOUT", f"Exceeded {timeout:g} seconds; partial counters unavailable",
                           (perf_counter() - started) * 1000)
        try:
            return receiver.recv()
        except (EOFError, OSError) as exc:
            return failure(path, "ERROR", f"Worker exited without a report: {exc}",
                           (perf_counter() - started) * 1000)
    except (OSError, ValueError) as exc:
        return failure(path, "ERROR", f"Unable to run benchmark worker: {exc}",
                       (perf_counter() - started) * 1000)
    finally:
        receiver.close()
        sender.close()
        if process.pid is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=2)
            process.close()
