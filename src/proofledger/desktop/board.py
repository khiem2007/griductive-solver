import tkinter as tk
from tkinter import ttk

from proofledger.contracts.values import Verdict
from proofledger.desktop import appearance as a
from proofledger.desktop.notebook import describe


class Board(ttk.Frame):
    def __init__(self, parent, on_select):
        """Initialize an empty keyboard-accessible grid of investigation cards."""
        super().__init__(parent)
        self.on_select = on_select
        self.buttons = {}
        self.frames = {}
        self.statements = {}
        self.cells = ()
        self.size = 0

    def populate(self, snapshot):
        """Build card widgets and coordinate headers for a new public snapshot."""
        for child in self.winfo_children():
            child.destroy()
        self.buttons.clear()
        self.frames.clear()
        self.statements.clear()
        self.size = snapshot.size
        self.cells = tuple(p.cell for p in snapshot.people)
        for x in range(snapshot.size):
            self.columnconfigure(x + 1, weight=1, uniform="board")
            ttk.Label(self, text=chr(65 + x), anchor="center", style="Muted.TLabel").grid(
                row=0, column=x + 1, pady=(0, 4))
        for y in range(snapshot.size):
            ttk.Label(self, text=str(y + 1), width=2, style="Muted.TLabel").grid(row=y + 1, column=0)
        for index, person in enumerate(snapshot.people):
            row, column = divmod(index, snapshot.size)
            frame = tk.Frame(self, background=a.LINE, padx=2, pady=2)
            frame.grid(row=row + 1, column=column + 1, sticky="nsew", padx=3, pady=3)
            button = tk.Button(frame, text=f"{person.cell} · {person.name}\n{person.profession}\nFace down",
                               relief="flat", borderwidth=0,
                               background=a.SURFACE, foreground=a.INK, activebackground="#EBE7F9",
                               highlightthickness=2, highlightcolor=a.PRIMARY,
                               highlightbackground=a.SURFACE, width=1, wraplength=110,
                               command=lambda c=person.cell: self.on_select(c))
            button.pack(fill="both", expand=True)
            statement = tk.Label(frame, text="Statement sealed", background=a.PAPER,
                                 foreground=a.MUTED, wraplength=110, justify="left",
                                 anchor="nw", padx=5, pady=7, width=1, font="TkSmallCaptionFont")
            statement.pack(fill="both", expand=True)
            statement.bind("<Button-1>", lambda _, c=person.cell: self.on_select(c))
            frame.bind("<Configure>", lambda e, b=button, s=statement: self.wrap_card(e, b, s))
            for key, offset in (("Left", -1), ("Right", 1), ("Up", -snapshot.size),
                                ("Down", snapshot.size)):
                button.bind(f"<{key}>", lambda _, i=index, d=offset: self.move_focus(i, d))
            button.bind("<Return>", lambda _, c=person.cell: self.on_select(c))
            self.buttons[person.cell] = button
            self.frames[person.cell] = frame
            self.statements[person.cell] = statement

    @staticmethod
    def wrap_card(event, button, statement):
        """Adapt card text wrapping to the current frame width."""
        width = max(65, event.width - 16)
        button.configure(wraplength=width)
        statement.configure(wraplength=width)

    def move_focus(self, index, delta):
        """Move keyboard focus by a row or column offset within the board."""
        target = index + delta
        if 0 <= target < len(self.cells):
            self.buttons[self.cells[target]].focus_set()
        return "break"

    def focus_cell(self, cell):
        """Move keyboard focus to a known coordinate when available."""
        if cell in self.buttons:
            self.buttons[cell].focus_set()

    def refresh(self, investigation):
        """Render public statuses, clues, selection, and referenced cells."""
        snapshot = investigation.public
        known = dict(snapshot.facts)
        clues = dict(snapshot.clues)
        people = {person.cell: person for person in snapshot.people}
        for cell, button in self.buttons.items():
            status = known.get(cell)
            label = "◆ Criminal" if status == Verdict.CRIMINAL else (
                "○ Innocent" if status == Verdict.INNOCENT else "— UNKNOWN")
            foreground = a.CRIMINAL if status == Verdict.CRIMINAL else (
                a.INNOCENT if status == Verdict.INNOCENT else a.MUTED)
            person = people[cell]
            side = "Face up" if cell in clues else "Face down"
            button.configure(text=f"{cell} · {person.name}\n{person.profession}\n{label}\n{side}",
                             foreground=foreground)
            clue = clues.get(cell)
            self.statements[cell].configure(
                text=(clue.text or describe(clue)) if clue else "Statement sealed",
                background=a.SURFACE if clue else a.PAPER,
                foreground=a.INK if clue else a.MUTED,
            )
            color = a.PRIMARY if cell == investigation.selected else (
                a.OCHRE if cell in investigation.references else a.LINE)
            self.frames[cell].configure(background=color)
