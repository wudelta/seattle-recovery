# FILE: aurora/tests/test_minions.py
from django.test import SimpleTestCase
from aurora.minion_array.generate_python import run

class MinionArraySecurityTests(SimpleTestCase):
    """System validation suite protecting local disk boundaries from bad minion writes."""

    def test_python_minion_accepts_clean_syntax(self):
        """Verify that standard functional python strings pass validation without changes."""
        clean_code = (
            "def runtime_evaluation_vector():\n"
            "    return {'status': 'OPERATIONAL', 'cores': 2}\n"
        )
        result = run(clean_code, fallback_context="Unit Test Suite Execution")
        self.assertEqual(result, clean_code, "The python minion altered or dropped clean syntax strings.")

    def test_python_minion_traps_invalid_syntax(self):
        """Verify that broken syntax blocks are caught and wrapped in markdown error logs."""
        broken_code = (
            "def broken_compilation_loop()\n"  # Structural Defect: Missing closing colon ':'
            "    print('This will fail compile validation checks')\n"
        )
        result = run(broken_code, fallback_context="Unit Test Suite Execution")
        
        # Ensure the structural error block wrapper is present
        self.assertIn("<!-- Python Minion Compilation Exception Block -->", result)
        self.assertIn("Error Details", result)
