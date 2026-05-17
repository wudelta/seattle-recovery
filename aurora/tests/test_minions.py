# FILE: aurora/test_minions.py
"""
 AUTO-SPEC DOCUMENTATION - SYNCED: 2026-05-17T20:22:45.584164+00:00
 PROJECT ECOSYSTEM: AURORA
 FILE PATH: aurora/tests/test_minions.py
 TECHNICAL MATRIX: Python Module. Exported Logic Components: test_python_minion_accepts_clean_syntax, runtime_evaluation_vector, test_python_minion_traps_invalid_syntax, broken_compilation_loop

 ARCHITECTURAL FLOW DIAGRAM:
 ```mermaid
 graph TD
    A[test_minions.py] --> B(System Kernel)
    B --> C{Ecosystem Check}
    C -->|Project Bind| D[AURORA]
 ```
"""
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