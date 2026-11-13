import unittest

from proofledger.contracts.messages import PublicSnapshot
from proofledger.contracts.values import Clue, Person, Verdict
from proofledger.reasoning.compiler import Circuit, compile_snapshot


class EncoderValidationTests(unittest.TestCase):
    def test_invalid_structured_clues_are_rejected_without_json_import(self):
        clues = (
            Clue("bad", "FACT", ("A1",), target=Verdict.UNKNOWN),
            Clue("bad", "FACT", ("A1", "B1"), target=Verdict.INNOCENT),
            Clue("bad", "SAME", ("A1",)),
            Clue("bad", "DIFFERENT", ("A1", "A1")),
            Clue("bad", "IMPLIES", ("A1", "Z9")),
            Clue("bad", "EXACTLY", (), count=0),
            Clue("bad", "EXACTLY", ("A1",), count=-1),
            Clue("bad", "AT_MOST", ("A1",), count=2),
            Clue("bad", "AT_LEAST", ("A1",), count=True),
            Clue("bad", "AT_LEAST", ("A1",), count=0.5),
            Clue("bad", "PARITY", ("A1",), odd="ODD"),
            Clue("bad", "UNSUPPORTED", ("A1",)),
        )
        for clue in clues:
            with self.subTest(clue=clue), self.assertRaises(ValueError):
                Circuit(("A1", "B1")).statement(clue)

    def test_unknown_or_outside_known_verdicts_are_rejected(self):
        for fact in (("A1", Verdict.UNKNOWN), ("Z9", Verdict.INNOCENT)):
            snapshot = PublicSnapshot("s", 0, "p", 3, (Person("A1", "Ada", "Maker"),),
                                      (), (fact,))
            with self.subTest(fact=fact), self.assertRaises(ValueError):
                compile_snapshot(snapshot)
