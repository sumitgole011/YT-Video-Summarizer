"""Source and offline Flask checks for the YouTube Q&A API."""
import ast
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from YT_bot import ragbot

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

    def test_invalid_requests_do_not_initialize_pipeline(self):
        with patch.object(ragbot, "build_chain") as build:
            client = ragbot.app.test_client()
            for body in ({}, {"question": " "}, {"question": []}, []):
                self.assertEqual(client.post("/ask", json=body).status_code, 400)
            build.assert_not_called()

    def test_valid_requests_reuse_pipeline_and_trim_questions(self):
        chain = Mock()
        chain.invoke.return_value = "Answer"
        with patch.object(ragbot, "_chain", None), patch.object(
            ragbot, "build_chain", return_value=chain
        ) as build:
            client = ragbot.app.test_client()
            for _ in range(2):
                response = client.post("/ask", json={"question": "  Why?  "})
                self.assertEqual(response.json, {"answer": "Answer"})
            build.assert_called_once_with()
            self.assertEqual(chain.invoke.call_count, 2)
            chain.invoke.assert_called_with("Why?")

    def test_pipeline_initialization_failure_returns_503_and_can_retry(self):
        chain = Mock()
        chain.invoke.return_value = "Answer"
        with patch.object(ragbot, "_chain", None), patch.object(
            ragbot, "build_chain", side_effect=[TimeoutError("provider details"), chain]
        ) as build:
            client = ragbot.app.test_client()
            with self.assertLogs(ragbot.app.logger, level="WARNING") as log:
                failed = client.post("/ask", json={"question": "Why?"})
            self.assertEqual(failed.status_code, 503)
            self.assertEqual(failed.json, {
                "error": "The transcript and model are temporarily unavailable."
            })
            self.assertNotIn("provider details", "\n".join(log.output))
            recovered = client.post("/ask", json={"question": "Why?"})
            self.assertEqual(recovered.status_code, 200)
            self.assertEqual(recovered.json, {"answer": "Answer"})
            self.assertEqual(build.call_count, 2)

    def test_inference_failure_returns_json_and_keeps_the_initialized_pipeline(self):
        chain = Mock()
        chain.invoke.side_effect = [TimeoutError("provider details"), "Answer"]
        with patch.object(ragbot, "_chain", chain), patch.object(ragbot, "build_chain") as build:
            client = ragbot.app.test_client()
            with self.assertLogs(ragbot.app.logger, level="WARNING") as log:
                response = client.post("/ask", json={"question": "Why?"})
            self.assertEqual(response.status_code, 502)
            self.assertEqual(response.json, {"error": "The model could not answer this question right now."})
            self.assertNotIn("provider details", "\n".join(log.output))
            retry = client.post("/ask", json={"question": "Why?"})
            self.assertEqual(retry.status_code, 200)
            self.assertEqual(retry.json, {"answer": "Answer"})
            build.assert_not_called()

    def test_debug_disabled(self):
        self.assertIn("debug=False", self.source)

if __name__ == "__main__":
    unittest.main()
