import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from proofledger.investigation.automation import AutoPilot
from proofledger.cases.catalog import sample_directory
from proofledger.investigation.coordinator import Investigation
from proofledger.cases.import_json import PuzzleError, load_definition
from proofledger.contracts.values import Outcome
from proofledger.desktop import appearance
from proofledger.desktop.guidance import show_guide
from proofledger.desktop.library import Library
from proofledger.desktop.tasks import ReasoningTask, WorkerFailure
from proofledger.desktop.workspace import Workspace


class Shell:
    def __init__(self, root, directory=None):
        """Compose the application shell and initialize worker and automation state."""
        self.root = root
        self.root.title("Proof Ledger")
        self.root.geometry("1180x860")
        self.root.minsize(640, 600)
        appearance.configure(root)
        self.case = None
        self.task = ReasoningTask()
        self.auto = AutoPilot()
        self.mode = tk.StringVar(value="Hands-on")
        self.overlay = False
        self.closed = False
        self.header = ttk.Frame(root, padding=(12, 8))
        self.header.pack(fill="x")
        ttk.Button(self.header, text="Library", command=self.toggle_library).pack(side="left")
        ttk.Button(self.header, text="Guide", command=lambda: show_guide(root)).pack(side="right")
        for label in ("Observe", "Hands-on"):
            ttk.Radiobutton(self.header, text=label, variable=self.mode, value=label,
                            command=self.change_mode).pack(side="right", padx=8)
        self.body = ttk.Frame(root)
        self.body.pack(fill="both", expand=True)
        self.body.columnconfigure(1, weight=1)
        self.body.rowconfigure(0, weight=1)
        self.workspace = Workspace(self.body, self.select, self.submit, self.hint, self.run, self.reset)
        self.workspace.grid(row=0, column=1, sticky="nsew")
        self.library = Library(self.body, directory or sample_directory(), self.load, self.open_file,
                               lambda: show_guide(root))
        self.library.grid(row=0, column=0, sticky="ns")
        self.root.bind("<Configure>", self.layout)
        self.root.bind("<KeyPress>", self.key)
        self.root.bind_all("<MouseWheel>", self.wheel, add="+")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self._timer = self.root.after(60, self.poll)

    def say(self, message):
        """Display a user-facing status message in the fixed footer."""
        self.workspace.message.configure(text=message)

    def refresh(self):
        """Refresh visible controls from the current investigation state."""
        if self.case:
            self.workspace.refresh(self.case, self.mode.get() == "Observe", self.auto.running,
                                   self.task.busy)

    def load(self, path):
        """Validate and open a puzzle, then request its initial public analysis."""
        try:
            definition = load_definition(path)
        except PuzzleError as exc:
            messagebox.showerror("Unable to open investigation", str(exc), parent=self.root)
            return
        self.task.cancel()
        self.auto.stop()
        self.case = Investigation(definition)
        self.workspace.board.populate(self.case.public)
        self.overlay = False
        self._layout()
        self.request_analysis()
        self.say("Examining the starting evidence…")
        self.workspace.canvas.yview_moveto(0)

    def open_file(self):
        """Show the JSON file picker and load the chosen investigation."""
        path = filedialog.askopenfilename(parent=self.root, title="Open investigation JSON",
                                          filetypes=(("Investigation", "*.json"), ("All files", "*.*")))
        if path:
            self.load(path)

    def request_analysis(self):
        """Start isolated reasoning for the current public snapshot."""
        try:
            self.task.start(self.case.public)
        except Exception as exc:
            self.auto.stop()
            self.say(f"Analysis could not start: {exc}. Reset or reopen to retry.")
        self.refresh()

    def select(self, cell):
        """Select a card according to the active interaction mode."""
        if self.case and self.case.select(cell, observe=self.mode.get() == "Observe"):
            self.refresh()

    def change_mode(self):
        """Apply Hands-on or Observe selection rules and redraw the workspace."""
        if self.case and self.mode.get() == "Observe":
            if self.case.selected not in dict(self.case.public.facts):
                self.case.selected = self.case.evidence_owner = None
        self.refresh()

    def submit(self, verdict):
        """Submit a verdict for the selected cell through the game coordinator."""
        if self.case is None:
            return
        result = self.case.submit(self.case.selected, verdict)
        self.after_verdict(result)

    def after_verdict(self, result):
        """Update messages, analysis, and automation after a verdict outcome."""
        messages = {
            Outcome.NOT_PROVABLE: "NOT_PROVABLE: both verdicts remain possible; the statement stays sealed.",
            Outcome.CONTRADICTED: "CONTRADICTED: the opposite verdict is proved; the statement stays sealed.",
            Outcome.INCONSISTENT: "INCONSISTENT: the evidence conflicts; no reveal is authorized.",
            Outcome.INVALID: "Choose an unresolved identity before proposing a verdict.",
            Outcome.PENDING: "Wait for the current evidence analysis to finish.",
        }
        if result == Outcome.ACCEPTED:
            self.say(f"{self.case.selected} is proved. Its statement is now in the ledger.")
            if self.case.public.solved:
                self.auto.stop()
                self.say("Investigation complete. Every identity has a proved verdict.")
            self.request_analysis()
        else:
            self.say(messages[result])
            if result == Outcome.INCONSISTENT:
                self.auto.stop()
        self.refresh()

    def hint(self):
        """Focus and explain the first currently provable unresolved identity."""
        if not self.case or self.task.busy:
            return
        analysis = self.case.analysis
        if analysis is None:
            self.say("Analysis is unavailable. Reset to retry.")
            return
        if analysis.inconsistent:
            self.say("INCONSISTENT: the published evidence conflicts; no hint can be justified.")
            return
        move = self.case.hint()
        if move is None:
            self.say("UNKNOWN: no unresolved verdict follows from the current evidence.")
        else:
            cell, verdict = move
            self.case.selected = cell
            self.case.evidence_owner = None
            related = [owner for owner, clue in self.case.public.clues if cell in clue.cells]
            suffix = f" Referencing statements: {', '.join(related)}." if related else ""
            self.say(f"The evidence establishes {cell} as {verdict.value.lower()}.{suffix}")
            self.workspace.board.focus_cell(cell)
            self.refresh()

    def run(self):
        """Toggle clock-driven automatic submission of forced verdicts."""
        if not self.case:
            return
        if self.auto.running:
            self.auto.stop()
            self.say("Deduction paused; your evidence is retained.")
        elif self.auto.start(self.case, time.monotonic()):
            self.say("Following provable verdicts, one statement at a time…")
        else:
            self.say(self.auto.reason)
        self.refresh()

    def reset(self):
        """Cancel work and restore the current puzzle's starting evidence."""
        if self.case:
            self.task.cancel()
            self.auto.stop()
            self.case.reset()
            self.request_analysis()
            self.say("Restored the starting evidence. Previous deductions were cleared.")

    def poll(self):
        """Poll background reasoning and advance automation without blocking Tk."""
        if self.closed:
            return
        result = self.task.poll()
        if isinstance(result, WorkerFailure):
            self.auto.stop()
            self.say(f"Analysis failed: {result.message}. Reset to retry.")
            self.refresh()
        elif result is not None and self.case and self.case.receive(result):
            if self.case.public.solved:
                self.say("Investigation complete. Every identity has a proved verdict.")
            elif not self.auto.running:
                self.say("Evidence ready. Inspect a statement or propose a proved verdict.")
            self.refresh()
        if self.case and self.auto.running:
            outcome = self.auto.tick(self.case, time.monotonic())
            if outcome is not None:
                self.after_verdict(outcome)
            elif not self.auto.running:
                self.say(self.auto.reason)
                self.refresh()
        self._timer = self.root.after(60, self.poll)

    def _layout(self):
        """Choose docked or overlay library placement for the current window width."""
        wide = self.root.winfo_width() >= 1100
        if wide:
            self.library.place_forget()
            self.library.grid(row=0, column=0, sticky="ns")
        else:
            self.library.grid_remove()
            if self.overlay:
                self.library.place(x=0, y=0, width=290, relheight=1)
                self.library.lift()
            else:
                self.library.place_forget()

    def layout(self, event):
        """Recompute responsive layout when the root window is configured."""
        if event.widget == self.root:
            self._layout()

    def toggle_library(self):
        """Toggle and focus the library overlay on narrow layouts."""
        self.overlay = not self.overlay
        self._layout()
        self.library.listbox.focus_set()

    def key(self, event):
        """Dispatch global shortcuts while leaving editable widgets untouched."""
        if isinstance(event.widget, (tk.Entry, ttk.Entry, ttk.Combobox)) or (
                isinstance(event.widget, tk.Text) and event.widget.cget("state") == "normal"):
            return
        action = {"h": self.hint, "a": self.run, "r": self.reset}.get(event.keysym.lower())
        if event.keysym == "Escape":
            self.auto.stop()
            self.overlay = True
            self._layout()
            self.library.listbox.focus_set()
            self.refresh()
        elif action:
            action()

    def wheel(self, event):
        """Scroll the workspace canvas for wheel events over non-text widgets."""
        if str(event.widget).startswith(str(self.workspace)) and not isinstance(event.widget, tk.Text):
            self.workspace.canvas.yview_scroll(-int(event.delta / 120), "units")

    def close(self):
        """Cancel callbacks and child work before destroying the Tk root."""
        self.closed = True
        self.root.after_cancel(self._timer)
        self.auto.stop()
        self.task.cancel()
        self.root.destroy()
