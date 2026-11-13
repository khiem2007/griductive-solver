import tkinter.font as tkfont
from tkinter import ttk

PAPER = "#F6F2E9"
SURFACE = "#FFFFFF"
INK = "#252A34"
MUTED = "#5D6570"
PRIMARY = "#493FA8"
OCHRE = "#A66A16"
CRIMINAL = "#783D68"
INNOCENT = "#236C88"
LINE = "#D7D2C9"


def configure(root):
    """Apply the shared Tk/ttk color, typography, and widget style system."""
    families = tkfont.families(root)
    family = "Segoe UI" if "Segoe UI" in families else "TkDefaultFont"
    tkfont.nametofont("TkDefaultFont").configure(family=family, size=11)
    tkfont.nametofont("TkTextFont").configure(family=family, size=11)
    root.configure(background=PAPER)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", background=PAPER, foreground=INK, font=(family, 11))
    style.configure("TButton", padding=(10, 7))
    style.map("TButton", background=[("active", "#E8E2F7")])
    style.configure("Primary.TButton", background=PRIMARY, foreground="white")
    style.map("Primary.TButton", background=[("active", "#392E8B"), ("disabled", LINE)],
              foreground=[("disabled", MUTED)])
    style.configure("Title.TLabel", font=(family, 22, "bold"))
    style.configure("Heading.TLabel", font=(family, 14, "bold"))
    style.configure("Muted.TLabel", foreground=MUTED)
    style.configure("TNotebook.Tab", padding=(15, 7))
    return family
