# ======================================================================
# FILE: aurora/tests/test_inspector.py (PATCH 1 OF 1)
# START: VALIDATION INSPECTOR LOCAL EXECUTION TEST SUITE
# ======================================================================
from django.test import TestCase
from unittest.mock import patch, MagicMock
from aurora.inspector import ValidationInspector

class ValidationInspectorTests(TestCase):
    """Test suite ensuring rapid native AST parsing and subprocess Ruff inspection loops."""

    def test_valid_python_syntax_passes_ast_inspection(self):
        """Syntax Check: Well-formed Python code strings must pass evaluation with zero defects."""
        clean_code = "def initialize_node():\n    return True\n"
        
        # Patch subprocess to simulate Ruff reporting no errors
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = "[]"
            mock_run.return_value = mock_proc
            
            results = ValidationInspector.check_syntax_and_imports(clean_code)
            self.assertTrue(results["valid"])
            self.assertEqual(len(results["errors"]), 0)

    def test_broken_python_syntax_fails_ast_immediately(self):
        """Syntax Check: Broken syntax must abort processing at Tier 1 without running subprocesses."""
        broken_code = "def broken_node(\n    print('missing paren')"
        
        with patch("subprocess.run") as mock_run:
            results = ValidationInspector.check_syntax_and_imports(broken_code)
            self.assertFalse(results["valid"])
            self.assertTrue(any("Syntax Error" in err for err in results["errors"]))
            # Assert Tier 2 subprocess runner was bypassed entirely
            mock_run.assert_not_called()

    @patch("subprocess.run")
    def test_ruff_violations_parse_into_errors_and_warnings(self, mock_run):
        """Metric Check: Core errors (E/F) must invalidate builds, while linting states report as warnings."""
        mock_violations = [
            {
                "code": "F401",
                "message": "os imported but unused",
                "location": {"row": 1, "column": 1}
            },
            {
                "code": "W292",
                "message": "no newline at end of file",
                "location": {"row": 4, "column": 1}
            }
        ]
        
        mock_proc = MagicMock()
        import json
        mock_proc.stdout = json.dumps(mock_violations)
        mock_run.return_value = mock_proc
        
        test_code = "import os\n\ndef run():\n    pass"
        results = ValidationInspector.check_syntax_and_imports(test_code)
        
        # F401 starts with F -> should trigger valid=False
        self.assertFalse(results["valid"])
        self.assertEqual(len(results["errors"]), 1)
        self.assertIn("[F401]", results["errors"][0])
        
        # W292 does not start with E/F -> should record as warning
        self.assertEqual(len(results["warnings"]), 1)
        self.assertIn("[W292]", results["warnings"][0])

    @patch("subprocess.run")
    def test_ruff_missing_binary_falls_back_gracefully(self, mock_run):
        """Guardrail Check: Missing systems paths must append localized alerts to warnings instead of crashing."""
        mock_run.side_effect = FileNotFoundError()
        
        test_code = "x = 10\n"
        results = ValidationInspector.check_syntax_and_imports(test_code)
        
        self.assertTrue(results["valid"])
        self.assertTrue(any("'ruff' binary not found" in warn for warn in results["warnings"]))
# ======================================================================
# END: VALIDATION INSPECTOR LOCAL EXECUTION TEST SUITE
# ======================================================================
