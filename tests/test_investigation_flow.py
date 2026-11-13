import dataclasses
import unittest

from helpers import puzzle

from proofledger.investigation.coordinator import Investigation
from proofledger.cases.import_json import parse_definition
from proofledger.contracts.values import Outcome, Verdict
from proofledger.reasoning.inference import analyze


class FlowTests(unittest.TestCase):
    def fresh(self, raw=None):
        case = Investigation(parse_definition(raw or puzzle()))
        case.receive(analyze(case.public))
        return case

    def test_initial_reveal_and_rejections_are_atomic(self):
        case = self.fresh()
        initial = case.public
        self.assertEqual(("A1",), tuple(c for c, _ in initial.clues))
        self.assertEqual(("A1",), tuple(c for c, _ in initial.facts))
        self.assertEqual(Outcome.NOT_PROVABLE, case.submit("C3", Verdict.INNOCENT))
        self.assertEqual(Outcome.CONTRADICTED, case.submit("B1", Verdict.CRIMINAL))
        self.assertEqual(initial, case.public)
        self.assertEqual((), case.journal)
        self.assertEqual(Outcome.ACCEPTED, case.submit("B1", Verdict.INNOCENT))
        self.assertEqual(2, len(case.public.clues))
        self.assertEqual(2, len(case.public.facts))
        self.assertEqual(("e0",), case.journal[0].active_clues)
        self.assertEqual("e1", case.journal[0].revealed_clue)
        self.assertEqual(Outcome.INVALID, case.submit("B1", Verdict.INNOCENT))
        self.assertEqual(Outcome.PENDING, case.submit("C1", Verdict.INNOCENT))

    def test_hidden_evidence_does_not_enter_snapshot(self):
        changed = puzzle()
        changed["clues"]["C3"] = {"type": "EXACTLY", "id": "secret", "data": {
            "region": {"kind": "EXPLICIT", "cells": ["A1"]}, "k": 0}}
        first, second = self.fresh(), self.fresh(changed)
        self.assertEqual(first.public.clues, second.public.clues)
        self.assertEqual(first.analysis.classifications, second.analysis.classifications)
        self.assertFalse(hasattr(first.public, "solution"))
        self.assertNotIn("secret", repr(second.public))

    def test_stale_results_reset_and_case_isolation(self):
        case = self.fresh()
        before = case.public
        old = case.analysis
        case.submit("B1", Verdict.INNOCENT)
        self.assertFalse(case.receive(old))
        case.reset()
        self.assertEqual(before.clues, case.public.clues)
        self.assertEqual(before.facts, case.public.facts)
        self.assertEqual((), case.journal)
        self.assertFalse(case.receive(old))
        self.assertFalse(case.receive(self.fresh().analysis))

    def test_hint_does_not_reveal_and_inspection_policy(self):
        case = self.fresh()
        before = case.public
        self.assertEqual(("B1", Verdict.INNOCENT), case.hint())
        self.assertEqual(case.hint(), case.hint())
        self.assertEqual(before, case.public)
        self.assertTrue(case.select("A1"))
        self.assertEqual(("B1",), case.references)
        self.assertFalse(case.select("B1", observe=True))
        self.assertTrue(case.select("B1"))
        self.assertIsNone(case.evidence)
        self.assertEqual((), case.references)

    def test_inconsistent_result_and_private_mismatch_refuse_reveal(self):
        case = self.fresh()
        snapshot = case.public
        case.receive(dataclasses.replace(case.analysis, inconsistent=True))
        self.assertEqual(Outcome.INCONSISTENT, case.submit("B1", Verdict.INNOCENT))
        case.receive(dataclasses.replace(case.analysis, inconsistent=False,
                                        classifications=(("B1", Verdict.CRIMINAL),)))
        self.assertEqual(Outcome.INCONSISTENT, case.submit("B1", Verdict.CRIMINAL))
        self.assertEqual(snapshot, case.public)

    def test_initially_solved_board(self):
        raw = puzzle()
        raw["initially_revealed"] = list(raw["solution"])
        case = self.fresh(raw)
        self.assertTrue(case.public.solved)
        self.assertIsNone(case.hint())
