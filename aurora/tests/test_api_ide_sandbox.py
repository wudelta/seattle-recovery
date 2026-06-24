# ======================================================================
# FILE: aurora/tests/test_api_ide_sandbox.py (PATCH 1 OF 1)
# START: TWIN_TRACK_SANDBOX_INTEGRATION_TESTS
# ======================================================================
import json
from django.test import TestCase, Client

class AnamodSandboxAPITestCase(TestCase):
    def setUp(self):
        """Initialize standard isolated API request clients with literal paths."""
        self.client = Client()
        # Bound directly to the literal URL paths used by the AJAX front-end controller
        self.run_url = '/aurora/api/sandbox/run/'
        self.lint_url = '/aurora/api/sandbox/lint/'

    def test_lint_api_detects_broken_python_syntax(self):
        """Assert that the flake8 linter catches and isolates explicit errors."""
        broken_code = "def broken_syntax_test()\n    print('Missing a colon')"
        payload = {'code': broken_code}
        
        response = self.client.post(
            self.lint_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('errors', data)
        # Verify path trimming substitution logic replaces temporary filenames
        self.assertNotIn('/tmp', data['errors'])

    def test_run_api_executes_valid_code(self):
        """Assert that valid code executes inside the container and returns stdout."""
        valid_code = "print('ANAMOD_SANDBOX_SUCCESS')"
        payload = {'code': valid_code}
        
        response = self.client.post(
            self.run_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('output', data)

    def test_run_api_enforces_execution_timeout_limit(self):
        """Assert that a stalling script is killed cleanly by the container manager."""
        stalling_code = "import time\ntime.sleep(10)"
        payload = {'code': stalling_code}
        
        response = self.client.post(
            self.run_url,
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('output', data)
        self.assertIn('timed out or failed', data['output'].lower())
# ======================================================================
# END: TWIN_TRACK_SANDBOX_INTEGRATION_TESTS (PATCH 1 OF 1)
# ======================================================================
