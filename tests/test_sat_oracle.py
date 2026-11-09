import itertools
import random
import unittest

from proofledger.reasoning.compiler import Formula
from proofledger.reasoning.search import solve


class SatOracleTests(unittest.TestCase):
    def test_failed_first_branch_backtracks_to_complete_model(self):
        formula = Formula(("A1", "B1"), ((1, 2), (-1, 2), (-1, -2)), 2)
        result = solve(formula, pure=False)
        self.assertTrue(result.satisfiable)
        self.assertEqual((False, True), result.values)
        self.assertGreater(result.counters.decisions, 0)
        self.assertGreater(result.counters.backtracks, 0)

    def test_generated_formulas_and_models(self):
        rng = random.Random(7401)
        for _ in range(160):
            n = rng.randint(1, 5)
            clauses = tuple(tuple(rng.choice((-1, 1)) * rng.randint(1, n)
                                  for _ in range(rng.randint(0, 4)))
                            for _ in range(rng.randint(0, 10)))
            expected = any(all(any(bits[abs(v) - 1] == (v > 0) for v in clause)
                               for clause in clauses)
                           for bits in itertools.product((False, True), repeat=n))
            for pure in (False, True):
                result = solve(Formula(tuple(str(i) for i in range(n)), clauses, n), pure=pure)
                self.assertEqual(expected, result.satisfiable, (clauses, pure))
                if result.satisfiable:
                    self.assertTrue(all(any(result.values[abs(v) - 1] == (v > 0)
                                            for v in clause) for clause in clauses))

    def test_assumptions_and_empty_cases(self):
        empty = Formula(("A1",), (), 1)
        self.assertTrue(solve(empty).satisfiable)
        self.assertFalse(solve(empty, (1, -1)).satisfiable)
        self.assertFalse(solve(Formula(("A1",), ((),), 1)).satisfiable)
