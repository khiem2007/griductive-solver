import csv
import json
from pathlib import Path

from proofledger.reports.runner import Report

METRIC_COLUMNS = (
    "puzzle", "size", "primary_variables", "auxiliary_variables", "full_clauses", "sat_calls",
    "decisions", "propagations", "backtracks", "pure_literals", "deduction_steps", "solved",
    "uniqueness", "runtime_ms", "status", "error", "source_file",
)
ABLATION_COLUMNS = (
    "puzzle", "decisions_off", "decisions_on", "propagations_off", "propagations_on",
    "backtracks_off", "backtracks_on", "pure_literals_on", "runtime_ms_off", "runtime_ms_on",
    "status_off", "status_on", "error_off", "error_on", "source_file",
)


def write_csv(path, columns, rows):
    """Write rows using a fixed, explicit CSV column contract."""
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def export_reports(directory: Path, reports: list[Report], without_pure: list[Report]):
    """Export metrics, deduction traces, and the pure-literal ablation comparison."""
    identifiers = [report.metrics["puzzle"] for report in reports]
    on_inputs = [r.metrics["source_file"] or r.metrics["puzzle"] for r in reports]
    off_inputs = [r.metrics["source_file"] or r.metrics["puzzle"] for r in without_pure]
    if on_inputs != off_inputs or len(set(on_inputs)) != len(on_inputs):
        raise ValueError("Optimization comparison must use the same ordered puzzle set")
    directory.mkdir(parents=True, exist_ok=True)
    write_csv(directory / "experiments.csv", METRIC_COLUMNS, [r.metrics for r in reports])
    traces = {}
    for index, report in enumerate(reports):
        key = report.metrics["puzzle"]
        if identifiers.count(key) > 1:
            key += f"@{report.metrics['source_file']}"
        while key in traces:
            key += f"@{index}"
        traces[key] = list(report.trace)
    (directory / "deduction_traces.json").write_text(
        json.dumps(traces, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    comparison = []
    for on, off in zip(reports, without_pure):
        row = {"puzzle": on.metrics["puzzle"], "source_file": on.metrics["source_file"]}
        for counter in ("decisions", "propagations", "backtracks", "runtime_ms"):
            row[f"{counter}_off"] = off.metrics[counter]
            row[f"{counter}_on"] = on.metrics[counter]
        row["pure_literals_on"] = on.metrics["pure_literals"]
        for field in ("status", "error"):
            row[f"{field}_off"] = off.metrics[field]
            row[f"{field}_on"] = on.metrics[field]
        comparison.append(row)
    write_csv(directory / "pure_literal_ablation.csv", ABLATION_COLUMNS, comparison)
