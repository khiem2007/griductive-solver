import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from helpers import puzzle

from proofledger.investigation.coordinator import Investigation
from proofledger.cases.import_json import parse_definition
from proofledger.reasoning.inference import analyze
from proofledger.desktop.shell import Shell


class DesktopTests(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.folder = tempfile.TemporaryDirectory()
        self.app = Shell(self.root, Path(self.folder.name))
        self.app.case = Investigation(parse_definition(puzzle(5)))
        self.app.case.receive(analyze(self.app.case.public))
        self.app.workspace.board.populate(self.app.case.public)
        self.app.refresh()
        self.root.update_idletasks()

    def tearDown(self):
        self.app.close()
        self.folder.cleanup()

    def test_adaptive_layout_preserves_board_and_scrolls(self):
        self.root.deiconify()
        for width in (640, 800, 1100):
            self.root.geometry(f"{width}x600")
            self.root.update()
            self.app._layout()
            self.root.update()
            self.assertEqual(25, len(self.app.workspace.board.buttons))
            right = self.app.workspace.board.buttons["E5"]
            self.assertLessEqual(right.winfo_rootx() + right.winfo_width(),
                                 self.root.winfo_rootx() + self.root.winfo_width())
            self.assertGreater(self.app.workspace.canvas.bbox("all")[3],
                               self.app.workspace.canvas.winfo_height())
            for control in (self.app.workspace.run, self.app.workspace.message):
                self.assertGreaterEqual(control.winfo_rooty(), self.root.winfo_rooty())
                self.assertLessEqual(control.winfo_rooty() + control.winfo_height(),
                                     self.root.winfo_rooty() + self.root.winfo_height())
            if width < 1100:
                self.assertFalse(self.app.library.winfo_ismapped())
            else:
                self.assertTrue(self.app.library.winfo_ismapped())

    def test_observe_controls_and_reference_focus(self):
        self.app.select("A1")
        self.assertEqual(("B1",), self.app.case.references)
        self.app.workspace.board.focus_cell("B1")
        self.assertEqual("A1", self.app.case.evidence_owner)
        self.app.select("B1")
        self.app.mode.set("Observe")
        self.app.change_mode()
        self.assertIsNone(self.app.case.selected)
        self.assertEqual("", self.app.workspace.verdicts.winfo_manager())
        self.app.select("C1")
        self.assertIsNone(self.app.case.selected)

    def test_board_shows_identity_and_only_published_statements(self):
        from proofledger.contracts.values import Verdict

        for person in self.app.case.public.people:
            text = self.app.workspace.board.buttons[person.cell].cget("text")
            self.assertIn(person.name, text)
            self.assertIn(person.profession, text)
        self.assertIn("Face down", self.app.workspace.board.buttons["B1"].cget("text"))
        self.assertEqual("Statement sealed", self.app.workspace.board.statements["B1"].cget("text"))
        self.app.case.submit("B1", Verdict.INNOCENT)
        self.app.refresh()
        self.assertIn("Face up", self.app.workspace.board.buttons["B1"].cget("text"))
        self.assertIn("C1", self.app.workspace.board.statements["B1"].cget("text"))

    def test_failed_open_preserves_session(self):
        before = self.app.case.public
        with patch("proofledger.desktop.shell.messagebox.showerror") as show:
            self.app.load(Path(self.folder.name) / "absent.json")
        show.assert_called_once()
        self.assertEqual(before, self.app.case.public)

    def test_event_loop_runs_during_analysis_and_case_switch_cancels_work(self):
        from proofledger.cases.catalog import sample_directory

        self.app.load(sample_directory() / "05_5x5.json")
        heartbeat = []
        self.root.after(10, lambda: heartbeat.append(True))
        deadline = time.monotonic() + 2
        while not heartbeat and time.monotonic() < deadline:
            self.root.update()
            time.sleep(0.01)
        self.assertTrue(heartbeat)
        self.assertTrue(self.app.task.busy)
        previous_session = self.app.case.public.session
        self.app.load(sample_directory() / "01_3x3.json")
        deadline = time.monotonic() + 20
        while self.app.case.analysis is None and time.monotonic() < deadline:
            self.root.update()
            time.sleep(0.01)
        self.assertIsNotNone(self.app.case.analysis)
        self.assertNotEqual(previous_session, self.app.case.analysis.session)
        self.assertEqual(self.app.case.public.session, self.app.case.analysis.session)
        self.app.run()
        self.assertTrue(self.app.auto.running)
        self.app.reset()
        self.assertFalse(self.app.auto.running)
        self.assertEqual((), self.app.case.journal)
