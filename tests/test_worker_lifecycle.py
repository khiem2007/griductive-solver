import time
import unittest

from helpers import puzzle

from proofledger.investigation.coordinator import Investigation
from proofledger.cases.import_json import parse_definition
from proofledger.reasoning.inference import Analysis
from proofledger.desktop.tasks import ReasoningTask, WorkerFailure


class WorkerTests(unittest.TestCase):
    def test_spawn_result_and_cancel(self):
        case = Investigation(parse_definition(puzzle()))
        task = ReasoningTask()
        try:
            task.start(case.public)
            deadline = time.monotonic() + 20
            result = None
            while result is None and time.monotonic() < deadline:
                time.sleep(0.02)
                result = task.poll()
            self.assertIsInstance(result, Analysis)
            self.assertTrue(case.receive(result))
            self.assertFalse(task.busy)
            task.start(case.public)
            task.cancel()
            self.assertFalse(task.busy)
            self.assertIsNone(task.poll())
        finally:
            task.cancel()

    def test_worker_error_is_distinct_from_unsat(self):
        import dataclasses

        from proofledger.contracts.values import Clue

        snapshot = Investigation(parse_definition(puzzle())).public
        invalid = dataclasses.replace(snapshot, clues=(("A1", Clue("bad", "INVALID", ("A1",))),))
        task = ReasoningTask()
        try:
            task.start(invalid)
            deadline = time.monotonic() + 20
            result = None
            while result is None and time.monotonic() < deadline:
                time.sleep(0.02)
                result = task.poll()
            self.assertIsInstance(result, WorkerFailure)
            self.assertIn("ValueError", result.message)
        finally:
            task.cancel()
