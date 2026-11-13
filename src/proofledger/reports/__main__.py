import argparse
import math
import sys
from pathlib import Path

from proofledger.cases.catalog import sample_directory
from proofledger.reports.benchmark import run_limited
from proofledger.reports.export import export_reports


def main(argv=None):
    """Run bounded experiments for all JSON puzzles and export three reports."""
    parser = argparse.ArgumentParser(description="Run public-only deductions and export metrics")
    parser.add_argument("--puzzles", type=Path, default=sample_directory(), help="Directory of JSON cases")
    parser.add_argument("--output", type=Path, default=Path("output"), help="Directory for the three reports")
    parser.add_argument("--timeout", type=float, default=30.0, help="Seconds allowed per input and mode")
    options = parser.parse_args(argv)
    try:
        paths = sorted(options.puzzles.glob("*.json"))
        if not paths:
            raise ValueError(f"No JSON investigations in {options.puzzles}")
        if not math.isfinite(options.timeout) or options.timeout <= 0:
            raise ValueError("Timeout must be positive")
        reports = [run_limited(path, pure=True, timeout=options.timeout) for path in paths]
        without_pure = [run_limited(path, pure=False, timeout=options.timeout) for path in paths]
        export_reports(options.output, reports, without_pure)
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"Report failed: {exc}", file=sys.stderr)
        return 2
    for report in reports:
        row = report.metrics
        print(f"{row['puzzle']}: {row['status']} steps={row['deduction_steps']} "
              f"all-clue models={row['uniqueness']} time={row['runtime_ms']:.3f} ms")
        if row["error"]:
            print(f"  {row['error']}")
    print(f"Wrote 3 reports to {options.output.resolve()}")
    return 0 if all(r.metrics["status"] == "SOLVED" for r in reports + without_pure) else 1


if __name__ == "__main__":
    raise SystemExit(main())
