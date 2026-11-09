import unittest

from helpers import puzzle

from proofledger.cases.import_json import parse_definition
from proofledger.contracts.values import Outcome
from proofledger.investigation.automation import AutoPilot
from proofledger.investigation.coordinator import Investigation
from proofledger.reasoning.inference import analyze


class AutomationTests(unittest.TestCase):
    def test_pause_resume_and_no_catchup_burst(self):
        case = Investigation(parse_definition(puzzle()))
        auto = AutoPilot()
        self.assertFalse(auto.start(case, 0))
        case.receive(analyze(case.public))
        self.assertTrue(auto.start(case, 0))
        self.assertEqual(Outcome.ACCEPTED, auto.tick(case, 0))
        self.assertIsNone(auto.tick(case, 100))  # Await new evidence analysis.
        case.receive(analyze(case.public))
        auto.stop()
        self.assertIsNone(auto.tick(case, 100))
        self.assertTrue(auto.start(case, 100))
        self.assertEqual(Outcome.ACCEPTED, auto.tick(case, 100))
        case.receive(analyze(case.public))
        self.assertIsNone(auto.tick(case, 100.1))
        self.assertEqual(2, len(case.journal))
        auto.stop()
        case.reset()
        self.assertFalse(auto.running)

    def test_complete_and_stalled_cases_stop(self):
        case = Investigation(parse_definition(puzzle()))
        auto = AutoPilot(0)
        case.receive(analyze(case.public))
        auto.start(case, 0)
        for _ in range(10):
            auto.tick(case, 0)
            case.receive(analyze(case.public))
        self.assertTrue(case.public.solved)
        self.assertFalse(auto.running)
        self.assertEqual(8, len(case.journal))
        raw = puzzle()
        raw["initially_revealed"] = []
        stalled = Investigation(parse_definition(raw))
        stalled.receive(analyze(stalled.public))
        auto.start(stalled, 0)
        auto.tick(stalled, 0)
        self.assertFalse(auto.running)
        self.assertEqual((), stalled.journal)
