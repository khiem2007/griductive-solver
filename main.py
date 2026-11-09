"""Course submission entry point: python main.py, without package installation."""
import multiprocessing
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

if __name__ == "__main__":
    multiprocessing.freeze_support()
    from proofledger.launch import main

    main()
