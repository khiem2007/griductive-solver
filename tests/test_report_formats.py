import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from helpers import puzzle

from proofledger.cases.catalog import sample_directory
from proofledger.cases.import_json import parse_definition
from proofledger.reports.__main__ import main
from proofledger.reports.export import ABLATION_COLUMNS, METRIC_COLUMNS, export_reports
from proofledger.reports.runner import run_definition


class ReportTests(unittest.TestCase):
    def test_trace_schema_and_metrics(self):
        report = run_definition(parse_definition(puzzle()))
        self.assertEqual(set(METRIC_COLUMNS), set(report.metrics))
        self.assertTrue(report.metrics["solved"])
        self.assertEqual("UNIQUE", report.metrics["uniqueness"])
        self.assertEqual(8, len(report.trace))
        self.assertEqual(["e0"], report.trace[0]["active_clues"])
        self.assertEqual("B1", report.trace[0]["cell"])
        self.assertEqual("INNOCENT", report.trace[0]["verdict"])
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            export_reports(root, [report], [run_definition(parse_definition(puzzle()), False)])
            with (root / "experiments.csv").open(encoding="utf-8", newline="") as stream:
                reader = csv.DictReader(stream)
                self.assertEqual(list(METRIC_COLUMNS), reader.fieldnames)
                self.assertEqual("True", next(reader)["solved"])
            with (root / "pure_literal_ablation.csv").open(encoding="utf-8", newline="") as stream:
                self.assertEqual(list(ABLATION_COLUMNS), csv.DictReader(stream).fieldnames)
            self.assertEqual(list(report.trace), json.loads(
                (root / "deduction_traces.json").read_text(encoding="utf-8"))["fixture"])

    def test_no_input_errors_and_duplicate_ids_keep_separate_rows(self):
        with (tempfile.TemporaryDirectory() as folder,
              contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO())):
            self.assertEqual(2, main(["--puzzles", folder, "--output", str(Path(folder) / "out")]))
            for filename in ("a.json", "b.json"):
                (Path(folder) / filename).write_text(json.dumps(puzzle()), encoding="utf-8")
            self.assertEqual(0, main(["--puzzles", folder, "--output", str(Path(folder) / "out")]))
            traces = json.loads((Path(folder) / "out/deduction_traces.json").read_text(encoding="utf-8"))
            self.assertEqual({"fixture@a.json", "fixture@b.json"}, set(traces))

    def test_samples_complete_with_and_without_pure_literals(self):
        from proofledger.cases.import_json import load_definition

        paths = sorted(sample_directory().glob("*.json"))
        self.assertEqual(6, len(paths))
        self.assertEqual([3, 3, 4, 4, 5, 5], [load_definition(p).size for p in paths])
        for path in paths:
            definition = load_definition(path)
            on = run_definition(definition)
            off = run_definition(definition, False)
            self.assertTrue(on.metrics["solved"], path)
            self.assertTrue(off.metrics["solved"], path)
            self.assertEqual(on.trace, off.trace)

    def test_stalled_case_is_reported_unsolved(self):
        raw = puzzle()
        raw["initially_revealed"] = []
        report = run_definition(parse_definition(raw))
        self.assertFalse(report.metrics["solved"])
        self.assertEqual((), report.trace)
        self.assertEqual("STALLED", report.metrics["status"])

    def test_trace_carries_actual_sat_assumptions_and_revealed_statement(self):
        report = run_definition(parse_definition(puzzle()))
        for entry in report.trace:
            self.assertEqual(entry["sat_calls"], len(entry["sat_queries"]))
            self.assertEqual("SAT", entry["sat_queries"][0]["result"])
            queries = [q for q in entry["sat_queries"] if q["cell"] == entry["cell"]]
            self.assertEqual(2, len(queries))
            self.assertEqual("UNSAT", next(q["result"] for q in queries
                                           if q["purpose"] == "assume_criminal"))
            self.assertEqual(entry["revealed_clue"], entry["revealed_statement"]["identifier"])

    def test_invalid_and_timed_out_runs_are_retained(self):
        from dataclasses import replace

        from proofledger.reports.benchmark import run_limited

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bad = root / "broken.json"
            bad.write_text("{bad json", encoding="utf-8")
            invalid = run_limited(bad, True, 10)
            self.assertEqual("INVALID", invalid.metrics["status"])
            good = root / "different_file_name.json"
            good.write_text(json.dumps(puzzle()), encoding="utf-8")
            timed_out = run_limited(good, True, 0.000001)
            self.assertEqual("TIMEOUT", timed_out.metrics["status"])
            self.assertIsNone(timed_out.metrics["sat_calls"])
            successful = run_definition(parse_definition(puzzle()))
            successful = replace(successful, metrics={**successful.metrics, "source_file": good.name})
            export_reports(root / "out", [timed_out, invalid], [successful, invalid])
            with (root / "out/pure_literal_ablation.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(2, len(rows))
            self.assertEqual("TIMEOUT", rows[0]["status_on"])
            self.assertEqual("SOLVED", rows[0]["status_off"])
            self.assertEqual("INVALID", rows[1]["status_on"])

    def test_cli_keeps_invalid_inputs_in_both_comparisons(self):
        with (tempfile.TemporaryDirectory() as folder,
              contextlib.redirect_stdout(io.StringIO())):
            root = Path(folder)
            (root / "broken.json").write_text("not JSON", encoding="utf-8")
            self.assertEqual(1, main(["--puzzles", folder, "--output", str(root / "out")]))
            with (root / "out/experiments.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(1, len(rows))
            self.assertEqual("INVALID", rows[0]["status"])

    def test_small_sample_deductions_against_exhaustive_public_models(self):
        import itertools

        from proofledger.investigation.coordinator import Investigation
        from proofledger.cases.import_json import load_definition
        from proofledger.contracts.values import Outcome, Verdict
        from proofledger.reasoning.inference import analyze
        from proofledger.reasoning.truth import holds

        for path in sorted(sample_directory().glob('*3x3.json')):
            case = Investigation(load_definition(path))
            while not case.public.solved:
                snapshot = case.public
                cells = tuple(person.cell for person in snapshot.people)
                possibilities = {cell: set() for cell in cells}
                for bits in itertools.product((False, True), repeat=9):
                    model = {cell: Verdict.CRIMINAL if bit else Verdict.INNOCENT
                             for cell, bit in zip(cells, bits)}
                    if all(model[c] == v for c, v in snapshot.facts) and all(
                            holds(clue, model) for _, clue in snapshot.clues):
                        for cell in cells:
                            possibilities[cell].add(model[cell])
                analysis = analyze(snapshot)
                for cell, verdict in analysis.classifications:
                    expected = possibilities[cell]
                    self.assertEqual(next(iter(expected)) if len(expected) == 1 else Verdict.UNKNOWN,
                                     verdict, (path.name, snapshot.revision, cell))
                case.receive(analysis)
                move = case.hint()
                self.assertIsNotNone(move)
                self.assertEqual(Outcome.ACCEPTED, case.submit(*move))
