import multiprocessing


def main():
    multiprocessing.freeze_support()
    try:
        import tkinter as tk
    except ImportError as exc:
        raise SystemExit("Proof Ledger needs Tkinter. Install Python's Tk component and retry.") from exc
    from proofledger.desktop.shell import Shell

    root = tk.Tk()
    Shell(root)
    root.mainloop()


if __name__ == "__main__":
    main()
