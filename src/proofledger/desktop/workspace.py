import tkinter as tk
from tkinter import ttk

from proofledger.contracts.values import Verdict
from proofledger.desktop import appearance as a
from proofledger.desktop.board import Board
from proofledger.desktop.notebook import Notebook


class Workspace(ttk.Frame):
    def __init__(self, parent, on_select, on_verdict, on_hint, on_run, on_reset):
        super().__init__(parent)
        viewport = ttk.Frame(self)
        viewport.pack(fill="both", expand=True)
        footer = ttk.Frame(self, padding=(18, 6))
        footer.pack(fill="x")
        self.canvas = tk.Canvas(viewport, background=a.PAPER, highlightthickness=0)
        scroll = ttk.Scrollbar(viewport, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)
        self.content = ttk.Frame(self.canvas, padding=(18, 12))
        self.window = self.canvas.create_window(0, 0, window=self.content, anchor="nw")
        self.canvas.bind("<Configure>", self.resize)
        self.content.bind("<Configure>", lambda _: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.title = ttk.Label(self.content, text="A notebook for careful conclusions", style="Title.TLabel")
        self.title.pack(anchor="w")
        self.progress = ttk.Label(self.content, text="Open an investigation from the library.", style="Muted.TLabel")
        self.progress.pack(anchor="w", pady=(4, 14))
        self.board = Board(self.content, on_select)
        self.board.pack(fill="x")
        self.identity = ttk.Label(footer, text="", style="Heading.TLabel")
        self.identity.pack(anchor="w", pady=(0, 6))
        self.verdicts = ttk.Frame(footer)
        self.verdicts.pack(fill="x", pady=(0, 10))
        self.proposals = []
        for verdict in (Verdict.CRIMINAL, Verdict.INNOCENT):
            button = ttk.Button(self.verdicts, text=f"Prove {verdict.value.lower()}",
                                command=lambda v=verdict: on_verdict(v))
            button.pack(side="left", padx=(0, 8))
            self.proposals.append(button)
        self.notebook = Notebook(self.content, self.board.focus_cell)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        controls = self.controls = ttk.Frame(footer)
        controls.pack(fill="x")
        self.hint = ttk.Button(controls, text="Hint · H", command=on_hint)
        self.run = ttk.Button(controls, text="Auto Solve · A", style="Primary.TButton", command=on_run)
        self.reset = ttk.Button(controls, text="Restart · R", command=on_reset)
        for i, button in enumerate((self.hint, self.run, self.reset)):
            button.grid(row=0, column=i, sticky="ew", padx=(0, 8))
            controls.columnconfigure(i, weight=1)
        self.message = ttk.Label(footer, text="Your next investigation awaits.", wraplength=600,
                                 foreground=a.PRIMARY, padding=(0, 6))
        self.message.pack(fill="x")
        for button in (self.hint, self.run, self.reset, *self.proposals):
            button.state(["disabled"])

    def resize(self, event):
        self.canvas.itemconfigure(self.window, width=event.width)
        for widget in (self.title, self.progress, self.identity, self.message):
            widget.configure(wraplength=max(300, event.width - 50))

    def refresh(self, case, observe, running, busy):
        snapshot = case.public
        self.title.configure(text=case.title)
        self.progress.configure(text=f"{snapshot.size} × {snapshot.size}  /  "
                                f"{case.initial_count} starting statements  /  "
                                f"{len(snapshot.facts)} of {len(snapshot.people)} resolved\n"
                                f"{case.description}")
        self.board.refresh(case)
        person = next((p for p in snapshot.people if p.cell == case.selected), None)
        self.identity.configure(text=f"{person.cell} · {person.name} / {person.profession}"
                                if person else "Choose an identity to examine")
        if observe:
            self.verdicts.pack_forget()
        elif not self.verdicts.winfo_manager():
            self.verdicts.pack(fill="x", pady=(0, 10), before=self.controls)
        enabled = not busy and not snapshot.solved and case.analysis is not None
        selected = case.selected is not None and case.selected not in dict(snapshot.facts)
        for button in self.proposals:
            button.state(["!disabled"] if enabled and selected and not observe else ["disabled"])
        self.hint.state(["!disabled"] if enabled else ["disabled"])
        self.run.state(["!disabled"] if (enabled or running) else ["disabled"])
        self.reset.state(["!disabled"])
        self.run.configure(text="Pause · A" if running else "Auto Solve · A")
        self.notebook.refresh(case)
