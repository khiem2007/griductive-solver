"""Guard the assignment's public-only agent and GUI-independent algorithms."""
import ast
import subprocess
import sys
import unittest
from pathlib import Path

import proofledger


class ArchitectureTests(unittest.TestCase):
    def test_solver_core_imports_only_public_game_contracts(self):
        directory = Path(proofledger.__file__).parent / "reasoning"
        public_modules = {"proofledger.contracts.values", "proofledger.contracts.messages"}
        for path in directory.glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                modules = ([node.module or ""] if isinstance(node, ast.ImportFrom) else
                           [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
                for module in modules:
                    with self.subTest(file=path.name, module=module):
                        if module.startswith("proofledger.contracts"):
                            self.assertIn(module, public_modules)
                        if module.startswith("proofledger."):
                            self.assertTrue(module.startswith(("proofledger.contracts",
                                                               "proofledger.reasoning")))
                        self.assertFalse(module.startswith("tkinter"))

    def test_contracts_do_not_import_other_project_packages(self):
        directory = Path(proofledger.__file__).parent / "contracts"
        for path in directory.glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                modules = ([node.module or ""] if isinstance(node, ast.ImportFrom) else
                           [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
                for module in modules:
                    with self.subTest(file=path.name, module=module):
                        if module.startswith("proofledger"):
                            self.assertTrue(module.startswith("proofledger.contracts"))

    def test_headless_report_import_does_not_load_gui(self):
        result = subprocess.run(
            [sys.executable, "-c", "import sys; import proofledger.reports.runner; "
             "assert not any(m == 'tkinter' or m.startswith('proofledger.desktop') "
             "for m in sys.modules)"],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, result.returncode, result.stderr)
