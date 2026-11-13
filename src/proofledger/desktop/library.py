import tkinter as tk
from tkinter import ttk

from proofledger.cases.catalog import CatalogEntry, discover
from proofledger.desktop import appearance as a


class Library(ttk.Frame):
    def __init__(self, parent, directory, on_load, on_open, on_help):
        """Create the puzzle catalog, size filter, and navigation controls."""
        super().__init__(parent, padding=12)
        self.entries = discover(directory)
        self.on_load = on_load
        self.visible: list[CatalogEntry] = []
        ttk.Label(self, text="Proof Ledger", style="Heading.TLabel").pack(anchor="w")
        ttk.Label(self, text="INVESTIGATIONS", style="Muted.TLabel").pack(anchor="w", pady=(20, 6))
        self.filter = tk.StringVar(value="All sizes")
        selector = ttk.Combobox(self, textvariable=self.filter, state="readonly", width=18,
                                values=("All sizes", "3 × 3", "4 × 4", "5 × 5"))
        selector.pack(fill="x")
        selector.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        listing = ttk.Frame(self)
        listing.pack(fill="both", expand=True, pady=10)
        self.listbox = tk.Listbox(listing, background=a.SURFACE, foreground=a.INK,
                                  selectbackground=a.PRIMARY, selectforeground="white",
                                  relief="flat", width=23, exportselection=False, activestyle="dotbox")
        scroll = ttk.Scrollbar(listing, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.listbox.pack(fill="both", expand=True)
        self.listbox.bind("<Double-Button-1>", self.activate)
        self.listbox.bind("<Return>", self.activate)
        ttk.Button(self, text="Begin selected", style="Primary.TButton", command=self.activate).pack(fill="x")
        ttk.Button(self, text="Load JSON…", command=on_open).pack(fill="x", pady=8)
        ttk.Button(self, text="Deduction guide", command=on_help).pack(fill="x")
        self.refresh()

    def refresh(self):
        """Filter catalog entries by board size and refresh the listbox."""
        size = None if self.filter.get() == "All sizes" else int(self.filter.get()[0])
        self.visible = [e for e in self.entries if size is None or
                        (e.definition is not None and e.definition.size == size)]
        self.listbox.delete(0, "end")
        for entry in self.visible:
            text = (f"{entry.definition.size}×{entry.definition.size}  {entry.definition.title}"
                    if entry.definition else f"! {entry.path.name}")
            self.listbox.insert("end", text)
        if self.visible:
            self.listbox.selection_set(0)

    def activate(self, _event=None):
        """Load the selected valid catalog entry through the supplied callback."""
        selection = self.listbox.curselection()
        if selection:
            self.on_load(self.visible[selection[0]].path)
