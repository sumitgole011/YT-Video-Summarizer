"""Dependency-free source checks; these do not exercise the live model or transcript API."""
import ast
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "YT_bot" / "ragbot.py"

class ApiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_ask_route_exists(self):
        names = [node.name for node in ast.walk(self.tree) if isinstance(node, ast.FunctionDef)]
        self.assertIn("ask", names)

    def test_json_validation_present(self):
        self.assertIn("request.get_json(silent=True)", self.source)
        self.assertIn("A non-empty question is required.", self.source)

    def test_debug_disabled(self):
        self.assertIn("debug=False", self.source)

if __name__ == "__main__":
    unittest.main()
