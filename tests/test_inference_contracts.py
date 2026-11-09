import itertools
import unittest

from proofledger.contracts.messages import PublicSnapshot
from proofledger.contracts.values import Clue, Person, Verdict
from proofledger.reasoning.compiler import Formula
from proofledger.reasoning.inference import analyze, next_move, uniqueness
from proofledger.reasoning.truth import holds


def public(clues=(), facts=()):
    people = tuple(Person(c, c, "Tester") for c in ("A1", "B1", "C1"))
    return PublicSnapshot("s", 0, "p", 3, people, tuple(clues), tuple(facts))


class InferenceTests(unittest.TestCase):
    def test_classifications_against_exhaustive_models(self):
        cases = [(), (("A1", Clue("a", "SAME", ("A1", "B1"))),),
                 (("A1", Clue("a", "EXACTLY", ("A1", "B1", "C1"), count=0)),),
                 (("A1", Clue("a", "FACT", ("A1",), target=Verdict.CRIMINAL)),
                  ("B1", Clue("b", "DIFFERENT", ("A1", "B1"))))]
        for clues in cases:
            snapshot = public(clues)
            cells = tuple(p.cell for p in snapshot.people)
            models = []
            for bits in itertools.product((False, True), repeat=3):
                model = {c: Verdict.CRIMINAL if bit else Verdict.INNOCENT
                         for c, bit in zip(cells, bits)}
                if all(holds(clue, model) for _, clue in clues):
                    models.append(model)
            result = analyze(snapshot)
            for cell, verdict in result.classifications:
                possible = {model[cell] for model in models}
                self.assertEqual(next(iter(possible)) if len(possible) == 1 else Verdict.UNKNOWN,
                                 verdict)
            self.assertEqual("UNIQUE" if len(models) == 1 else "MULTIPLE", result.uniqueness)

    def test_inconsistency_is_not_entailment(self):
        snapshot = public((("A1", Clue("x", "FACT", ("A1",), target=Verdict.CRIMINAL)),),
                          (("A1", Verdict.INNOCENT),))
        result = analyze(snapshot)
        self.assertTrue(result.inconsistent)
        self.assertEqual("INCONSISTENT", result.uniqueness)
        self.assertIsNone(next_move(snapshot, result))

    def test_uniqueness_ignores_auxiliary_assignments(self):
        self.assertEqual("UNIQUE", uniqueness(Formula(("A1",), ((1,),), 2)))
        self.assertEqual("MULTIPLE", uniqueness(Formula(("A1",), (), 2)))

    def test_hint_chooses_first_unresolved(self):
        snapshot = public((("A1", Clue("x", "EXACTLY", ("A1", "B1", "C1"), count=0)),),
                          (("A1", Verdict.INNOCENT),))
        self.assertEqual(("B1", Verdict.INNOCENT), next_move(snapshot, analyze(snapshot)))
