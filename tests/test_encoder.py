import unittest
from itertools import product

from core.models import Character, Clue, Status
from core.regions import resolve_region
from logic.cnf_encoder import CNFEncoder
from logic.semantics import evaluate_clue


class EncoderTests(unittest.TestCase):
    def setUp(self):
        self.characters = {
            "A1": Character("A1", "A", "X"),
            "B1": Character("B1", "B", "Y"),
            "C1": Character("C1", "C", "Z"),
        }
        self.encoder = CNFEncoder(self.characters)

    def _cnf_value(self, clauses, assignment):
        variables = self.encoder.variable_map
        values = {
            variables[cell]: assignment[cell] == Status.CRIMINAL
            for cell in assignment
        }
        return all(any(values[abs(lit)] == (lit > 0) for lit in clause) for clause in clauses)

    def test_all_template_encodings_match_direct_semantics(self):
        region = {"kind": "EXPLICIT", "cells": ["A1", "B1", "C1"]}
        clues = [
            Clue("F", "FACT", {"cell": "A1", "status": "CRIMINAL"}),
            Clue("S", "SAME", {"a": "A1", "b": "B1"}),
            Clue("D", "DIFFERENT", {"a": "A1", "b": "B1"}),
            Clue("E", "EXACTLY", {"k": 2, "region": region}),
            Clue("L", "AT_LEAST", {"k": 2, "region": region}),
            Clue("M", "AT_MOST", {"k": 1, "region": region}),
            Clue("P", "PARITY", {"parity": "ODD", "region": region}),
            Clue("I", "IMPLIES", {"a": "A1", "b": "B1"}),
        ]
        for bits in product((Status.INNOCENT, Status.CRIMINAL), repeat=3):
            assignment = dict(zip(self.characters, bits))
            for clue in clues:
                with self.subTest(bits=bits, clue=clue.type):
                    clauses = self.encoder.encode_clue(clue, 3)
                    self.assertEqual(
                        self._cnf_value(clauses, assignment),
                        evaluate_clue(clue, assignment, 3),
                    )


class RegionEncodingTests(unittest.TestCase):
    """Counting clues must encode identically over every supported region kind."""

    def setUp(self):
        self.cells = [f"{chr(65 + c)}{r + 1}" for r in range(3) for c in range(3)]
        self.characters = {c: Character(c, c, "x") for c in self.cells}
        self.encoder = CNFEncoder(self.characters)

    def test_region_clues_match_direct_semantics(self):
        regions = [
            {"kind": "ROW", "index": 2},
            {"kind": "COLUMN", "index": "B"},
            {"kind": "NEIGHBORS", "cell": "B2"},
            {"kind": "NEIGHBORS", "cell": "A1"},
            {"kind": "CORNERS"},
            {"kind": "BOUNDARY"},
            {"kind": "EXPLICIT", "cells": ["A1", "B2", "C3"]},
        ]
        clues = []
        for region in regions:
            size = len(resolve_region(region, 3))
            for k in range(size + 1):
                clues.append(Clue("E", "EXACTLY", {"k": k, "region": region}))
                clues.append(Clue("L", "AT_LEAST", {"k": k, "region": region}))
                clues.append(Clue("M", "AT_MOST", {"k": k, "region": region}))
            for parity in ("ODD", "EVEN"):
                clues.append(Clue("P", "PARITY", {"parity": parity, "region": region}))

        variables = self.encoder.variable_map
        for bits in product((Status.INNOCENT, Status.CRIMINAL), repeat=9):
            assignment = dict(zip(self.cells, bits))
            values = {variables[c]: assignment[c] == Status.CRIMINAL for c in self.cells}
            for clue in clues:
                cnf = self.encoder.encode_clue(clue, 3)
                cnf_value = all(
                    any(values[abs(lit)] == (lit > 0) for lit in clause)
                    for clause in cnf
                )
                if cnf_value != evaluate_clue(clue, assignment, 3):
                    self.fail(f"{clue.type} {clue.data} disagrees on {assignment}")


if __name__ == "__main__":
    unittest.main()
