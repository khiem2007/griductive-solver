import tkinter as tk
from tkinter import ttk

from proofledger.desktop.notebook import Notebook

GUIDE = """Build a verdict from evidence

Each published identity contributes a known verdict and one truthful statement. A statement remains truthful regardless of its owner's verdict. Names and occupations are only identifiers.

Choose a coordinate, then propose a verdict. The ledger opens that identity only when every possibility consistent with the current evidence agrees. An answer can match the hidden solution and still lack proof.

A rejection distinguishes an undecided identity, an answer opposed by the evidence, or conflicting evidence. No rejected proposal opens a statement.

Use Hint for the first provable next verdict. Auto Solve repeats the same proof process and pauses when nothing more follows. Hint pointers and highlighted cells identify references, not a complete proof explanation.

Hands-on allows proposals. Observe lets you inspect published statements while automation handles deductions. Switching modes retains your investigation.

◆ Criminal   ○ Innocent   — Unresolved
Indigo outline: selected identity. Ochre outline: statement reference.

H: hint   A: run/pause   R: reset
Arrow keys: move board focus   Enter: select
Escape: pause and open library   Tab: next control
Shortcuts stay inactive while typing. Restart discards this session's deductions. Sessions are not saved when the app closes.

Analysis runs in an isolated process using only public evidence. These local puzzle files contain the answers; this is a logical boundary, not an anti-cheat system.
"""


def show_guide(root):
    """Open the non-modal deduction and keyboard-shortcut guide window."""
    window = tk.Toplevel(root)
    window.title("Proof Ledger · Deduction guide")
    window.geometry("650x650")
    window.minsize(450, 400)
    window.transient(root)
    reader = Notebook._reader(window, 20)
    Notebook.write(reader, GUIDE)
    ttk.Button(window, text="Return to investigation", command=window.destroy).pack(pady=10)
