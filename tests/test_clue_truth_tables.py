import itertools
import unittest

from proofledger.contracts.values import Clue, Verdict
from proofledger.reasoning.compiler import Circuit
from proofledger.reasoning.search import solve
from proofledger.reasoning.truth import holds


class ClueTables(unittest.TestCase):
    def test_every_supported_statement_against_all_assignments(self):
        cells = ("A1", "B1", "C1", "A2")
        clues = [Clue("t", "FACT", ("A1",), target=target)
                 for target in (Verdict.CRIMINAL, Verdict.INNOCENT)]
        clues += [Clue("t", kind, cells[:2]) for kind in ("SAME", "DIFFERENT", "IMPLIES")]
        clues += [Clue("t", kind, cells, count=k) for kind in
                  ("EXACTLY", "AT_LEAST", "AT_MOST") for k in range(5)]
        clues += [Clue("t", "PARITY", cells, odd=odd) for odd in (False, True)]
        for clue in clues:
            circuit = Circuit(cells)
            circuit.statement(clue)
            formula = circuit.finish()
            for bits in itertools.product((False, True), repeat=4):
                assignment = {c: Verdict.CRIMINAL if b else Verdict.INNOCENT
                              for c, b in zip(cells, bits)}
                expected = holds(clue, assignment)
                assumptions = tuple(i if bit else -i for i, bit in enumerate(bits, 1))
                with self.subTest(kind=clue.kind, k=clue.count, odd=clue.odd, bits=bits):
                    self.assertEqual(expected, solve(formula, assumptions).satisfiable)

    def test_parity_growth_is_linear(self):
        circuit = Circuit(tuple(f"P{i}" for i in range(16)))
        circuit.statement(Clue("p", "PARITY", circuit.cells, odd=True))
        self.assertLess(len(circuit.finish().clauses), 65)
