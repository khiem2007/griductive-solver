import unittest

from core.game_engine import GameEngine
from core.models import Character, Clue, Puzzle, PublicState, Status, VerdictResult
from core.regions import all_cells, resolve_region
from game.session import GameSession
from logic.agent import LogicAgent
from logic.semantics import validate_clue


def tiny_puzzle():
    """2x2 board whose chain stalls on purpose, so every verdict state is reachable."""
    cells = ["A1", "B1", "A2", "B2"]
    characters = {cell: Character(cell, cell.lower(), "tester") for cell in cells}
    solution = {
        "A1": Status.CRIMINAL, "B1": Status.INNOCENT,
        "A2": Status.INNOCENT, "B2": Status.CRIMINAL,
    }
    clues = {
        "A1": Clue("T1", "FACT", {"cell": "B1", "status": "INNOCENT"}),
        "B1": Clue("T2", "DIFFERENT", {"a": "A2", "b": "B2"}),
        "A2": Clue("T3", "FACT", {"cell": "B2", "status": "CRIMINAL"}),
        "B2": Clue("T4", "FACT", {"cell": "A1", "status": "CRIMINAL"}),
    }
    return Puzzle("tiny", "Tiny", 2, characters, solution, clues, ["A1"])


class RegionTests(unittest.TestCase):
    def test_every_supported_region_kind(self):
        self.assertEqual(resolve_region({"kind": "ROW", "index": 2}, 3),
                         ["A2", "B2", "C2"])
        self.assertEqual(resolve_region({"kind": "COLUMN", "index": "B"}, 3),
                         ["B1", "B2", "B3"])
        self.assertEqual(sorted(resolve_region({"kind": "NEIGHBORS", "cell": "A1"}, 3)),
                         ["A2", "B1", "B2"])
        self.assertEqual(len(resolve_region({"kind": "NEIGHBORS", "cell": "B2"}, 3)), 8)
        self.assertEqual(sorted(resolve_region({"kind": "CORNERS"}, 3)),
                         ["A1", "A3", "C1", "C3"])
        self.assertEqual(len(resolve_region({"kind": "BOUNDARY"}, 4)), 12)
        self.assertEqual(resolve_region({"kind": "EXPLICIT", "cells": ["a1", "c3"]}, 3),
                         ["A1", "C3"])

    def test_invalid_regions_and_parameters(self):
        for region in (
            {"kind": "ROW", "index": 9},                      # outside the board
            {"kind": "EXPLICIT", "cells": ["A1", "A1"]},      # duplicate cells
            {"kind": "EXPLICIT", "cells": []},                # empty
            {"kind": "DIAGONAL"},                             # unsupported
        ):
            with self.subTest(region=region), self.assertRaises(ValueError):
                resolve_region(region, 3)

    def test_counting_bound_is_validated(self):
        valid = set(all_cells(3))
        row = {"kind": "ROW", "index": 1}
        with self.assertRaises(ValueError):
            validate_clue(Clue("X", "EXACTLY", {"k": 4, "region": row}), 3, valid)
        with self.assertRaises(ValueError):
            validate_clue(Clue("X", "SAME", {"a": "A1", "b": "A1"}), 3, valid)
        with self.assertRaises(ValueError):
            validate_clue(Clue("X", "PARITY", {"parity": "MAYBE", "region": row}), 3, valid)
        validate_clue(Clue("X", "AT_MOST", {"k": 3, "region": row}), 3, valid)


class VerdictStateTests(unittest.TestCase):
    def setUp(self):
        self.session = GameSession(GameEngine(tiny_puzzle()), LogicAgent())

    def test_face_up_card_publishes_its_status_and_clue(self):
        public = self.session.public
        self.assertEqual(public.proved_statuses["A1"], Status.CRIMINAL)
        self.assertIn("A1", public.revealed_clues)
        self.assertNotIn("B1", public.revealed_clues)

    def test_contradicted_then_accepted_then_not_provable(self):
        # B1 is forced INNOCENT by the face-up clue.
        result, clue = self.session.submit("B1", Status.CRIMINAL)
        self.assertEqual(result, VerdictResult.CONTRADICTED)
        self.assertIsNone(clue)
        self.assertNotIn("B1", self.session.public.revealed_clues)

        result, clue = self.session.submit("B1", Status.INNOCENT)
        self.assertEqual(result, VerdictResult.ACCEPTED)
        self.assertEqual(clue.clue_id, "T2")

        # T2 only says A2 and B2 differ, so neither is forced yet.
        result, _ = self.session.submit("A2", Status.CRIMINAL)
        self.assertEqual(result, VerdictResult.NOT_PROVABLE)
        result, _ = self.session.submit("A2", Status.INNOCENT)
        self.assertEqual(result, VerdictResult.NOT_PROVABLE)

    def test_hint_never_points_at_an_unforced_character(self):
        agent = self.session.agent
        move = agent.next_forced(self.session.public, self.session.analysis)
        self.assertEqual(move, ("B1", Status.INNOCENT))
        self.session.submit(*move)
        self.assertIsNone(agent.next_forced(self.session.public, self.session.analysis))


class KnowledgeBaseTests(unittest.TestCase):
    def setUp(self):
        self.agent = LogicAgent()
        self.characters = {
            cell: Character(cell, cell.lower(), "tester")
            for cell in ["A1", "B1", "A2", "B2"]
        }

    def _state(self, clues):
        return PublicState("kb", 2, dict(self.characters),
                           {f"C{i}": clue for i, clue in enumerate(clues)}, {})

    def test_unsatisfiable_knowledge_base_is_reported(self):
        state = self._state([
            Clue("U1", "FACT", {"cell": "A1", "status": "CRIMINAL"}),
            Clue("U2", "FACT", {"cell": "A1", "status": "INNOCENT"}),
        ])
        analysis = self.agent.analyze(state)
        self.assertTrue(analysis.inconsistent)
        self.assertEqual(analysis.classifications, {})
        self.assertEqual(self.agent.uniqueness_check(state), "INCONSISTENT")

    def test_uniqueness_distinguishes_single_and_multiple_models(self):
        loose = self._state([Clue("M1", "FACT", {"cell": "A1", "status": "CRIMINAL"})])
        self.assertEqual(self.agent.uniqueness_check(loose), "MULTIPLE")

        pinned = self._state([
            Clue("S1", "FACT", {"cell": "A1", "status": "CRIMINAL"}),
            Clue("S2", "FACT", {"cell": "B1", "status": "INNOCENT"}),
            Clue("S3", "FACT", {"cell": "A2", "status": "INNOCENT"}),
            Clue("S4", "FACT", {"cell": "B2", "status": "CRIMINAL"}),
        ])
        self.assertEqual(self.agent.uniqueness_check(pinned), "UNIQUE")


class InconsistentSubmissionTests(unittest.TestCase):
    def test_engine_reports_inconsistent_instead_of_not_provable(self):
        session = GameSession(GameEngine(tiny_puzzle()), LogicAgent())
        session.analysis.inconsistent = True
        result, clue = session.submit("B1", Status.INNOCENT)
        self.assertEqual(result, VerdictResult.INCONSISTENT)
        self.assertIsNone(clue)


if __name__ == "__main__":
    unittest.main()
