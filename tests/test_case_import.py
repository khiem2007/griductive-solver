import json
import tempfile
import unittest
from pathlib import Path

from helpers import puzzle

from proofledger.cases.catalog import discover
from proofledger.cases.import_json import PuzzleError, load_definition, parse_definition


class ImportTests(unittest.TestCase):
    def test_names_follow_alphabetical_board_order(self):
        raw = puzzle()
        raw["characters"][0]["name"] = "Zulu"
        with self.assertRaisesRegex(PuzzleError, "alphabetically"):
            parse_definition(raw)

    def test_complete_clue_set_must_have_one_primary_assignment(self):
        raw = puzzle()
        cells = list(raw["solution"])
        for index, cell in enumerate(cells):
            raw["clues"][cell] = {"id": f"r{index}", "type": "SAME", "data": {
                "a": cell, "b": cells[(index + 1) % len(cells)]}}
        with self.assertRaisesRegex(PuzzleError, "exactly one"):
            parse_definition(raw)
        # A low-level diagnostic opt-out does not affect the normal GUI loader.
        self.assertEqual(9, len(parse_definition(raw, require_unique=False).people))

    def test_supported_sizes_and_frozen_clues(self):
        for size in (3, 4, 5):
            definition = parse_definition(puzzle(size))
            self.assertEqual(size * size, len(definition.people))
            with self.assertRaises(AttributeError):
                definition.clues[0][1].cells += ("B1",)

    def test_invalid_shapes_and_truth(self):
        changes = [lambda p: p.pop("id"),
                   lambda p: p.update(size=3.0),
                   lambda p: p["characters"].append(p["characters"][0]),
                   lambda p: p["solution"].update(A1="UNKNOWN"),
                   lambda p: p["initially_revealed"].append("a1"),
                   lambda p: p["clues"]["B1"].update(id="e0"),
                   lambda p: p["clues"]["A1"]["data"].update(status="CRIMINAL"),
                   lambda p: p["solution"].pop("A1")]
        for change in changes:
            data = puzzle()
            change(data)
            with self.subTest(change=change), self.assertRaises(PuzzleError):
                parse_definition(data)

    def test_catalog_isolates_bad_files_and_rejects_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "good.json").write_text(json.dumps(puzzle()), encoding="utf-8")
            (root / "bad.json").write_text('{"size":3,"size":4}', encoding="utf-8")
            entries = discover(root)
            self.assertEqual(2, len(entries))
            self.assertIn("Repeated JSON key", entries[0].error)
            self.assertIsNotNone(entries[1].definition)
            with self.assertRaises(PuzzleError):
                load_definition(root / "missing.json")

    def test_fractional_count_and_unknown_fact_fail(self):
        for data in ({"type": "FACT", "data": {"cell": "A1", "status": "UNKNOWN"}},
                     {"type": "AT_MOST", "data": {"k": 1.5, "region": {
                         "kind": "ROW", "index": 1}}}):
            raw = puzzle()
            raw["clues"]["A1"] = data
            with self.assertRaises(PuzzleError):
                parse_definition(raw)
