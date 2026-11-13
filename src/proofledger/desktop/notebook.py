import tkinter as tk
from dataclasses import fields
from tkinter import ttk

from proofledger.desktop import appearance as a


class Notebook(ttk.Notebook):
    def __init__(self, parent, focus_cell):
        """Create evidence, chronology, and solver-analysis tabs."""
        super().__init__(parent)
        self.focus_cell = focus_cell
        self.evidence = ttk.Frame(self, padding=12)
        self.history = ttk.Frame(self, padding=12)
        self.metrics = ttk.Frame(self, padding=12)
        for frame, title in ((self.evidence, "Evidence"), (self.history, "Chronology"),
                             (self.metrics, "Analysis")):
            self.add(frame, text=title)
        self.evidence_text = self._reader(self.evidence, 5)
        self.chips = ttk.Frame(self.evidence)
        self.chips.pack(fill="x", pady=(8, 0))
        self.history_text = self._reader(self.history, 7)
        self.metrics_text = self._reader(self.metrics, 7)

    @staticmethod
    def _reader(parent, height):
        """Create a read-only styled text widget with a vertical scrollbar."""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)
        text = tk.Text(frame, wrap="word", height=height, width=25, font="TkTextFont", background=a.SURFACE,
                       foreground=a.INK, relief="flat", padx=10, pady=8, state="disabled")
        scrollbar = ttk.Scrollbar(frame, command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
        return text

    @staticmethod
    def write(widget, content):
        """Replace a read-only text widget's contents without leaving it editable."""
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def refresh(self, investigation):
        """Render current public evidence, accepted steps, and analysis metrics."""
        clue = investigation.evidence
        text = "Choose a published identity to examine its statement. Unresolved evidence stays sealed."
        if clue:
            text = f"{clue.identifier} · {clue.kind}\n\n{clue.text or describe(clue)}"
        self.write(self.evidence_text, text)
        for child in self.chips.winfo_children():
            child.destroy()
        for i, cell in enumerate(investigation.references):
            ttk.Button(self.chips, text=cell, width=4,
                       command=lambda c=cell: self.focus_cell(c)).grid(
                           row=i // 7, column=i % 7, padx=2, pady=2)
        history = "\n\n".join(
            f"{entry.step:02}  {entry.cell} → {entry.verdict.value.lower()}\n"
            f"Active clues: {', '.join(entry.active_clues)}\n"
            + "\n".join(f"  {query.purpose}: {query.assumptions} → {query.result}"
                        for query in entry.sat_queries if query.cell == entry.cell)
            + f"\nPublished {entry.revealed_clue}: "
            + (entry.revealed_statement.text or describe(entry.revealed_statement))
            for entry in investigation.journal)
        self.write(self.history_text, history or "Your accepted deductions will be recorded here.")
        analysis = investigation.analysis
        if analysis is None:
            metrics = "Analyzing the current public evidence…"
        else:
            metrics = (f"Public possibilities: {analysis.uniqueness}\n"
                       f"Cell variables: {analysis.primary_variables}\n"
                       f"Circuit variables: {analysis.auxiliary_variables}\n"
                       f"Clauses: {analysis.clauses}\n\n")
            metrics += "\n".join(f"{field.name.replace('_', ' ').capitalize()}: "
                                 f"{getattr(analysis.counters, field.name):.3f}"
                                 if field.name == "runtime_ms" else
                                 f"{field.name.replace('_', ' ').capitalize()}: "
                                 f"{getattr(analysis.counters, field.name)}"
                                 for field in fields(analysis.counters))
            metrics += "\n\nCounters cover classification queries; uniqueness is excluded."
            metrics += "\n\nUnresolved classifications:\n" + "\n".join(
                f"{cell}: {verdict.value}" for cell, verdict in analysis.classifications
                if cell not in dict(investigation.public.facts))
            metrics += "\n\nSAT query log (signed row-major variables):\n" + "\n".join(
                f"{query.cell or 'KB'} / {query.purpose} / {query.assumptions} / {query.result}"
                for query in analysis.queries)
        self.write(self.metrics_text, metrics)


def describe(clue):
    """Convert a structured clue into concise natural-language display text."""
    cells = ", ".join(clue.cells)
    if clue.kind == "FACT":
        return f"{cells} has a {clue.target.value.lower()} verdict."
    if clue.kind == "SAME":
        return f"{cells} share a verdict."
    if clue.kind == "DIFFERENT":
        return f"{cells} have opposite verdicts."
    if clue.kind == "IMPLIES":
        return f"A criminal verdict for {clue.cells[0]} requires one for {clue.cells[1]}."
    if clue.kind == "PARITY":
        return f"An {'odd' if clue.odd else 'even'} number of criminals occupy {cells}."
    relation = {"EXACTLY": "Precisely", "AT_LEAST": "No fewer than", "AT_MOST": "No more than"}
    return f"{relation[clue.kind]} {clue.count} criminals occupy {cells}."
