# ======================================================================
# FILE: aurora/tests/test_ide_api.py (PATCH 1 OF 1)
# START: IDE_AND_SANDBOX_INTEGRATION_TESTS
# ======================================================================
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse

class TestIdeOperationsAndSandbox(TestCase):
    def setUp(self):
        self.client = Client()
        self.tree_url = reverse('aurora:ide_file_tree')
        self.op_url = reverse('aurora:ide_file_operations')
        self.run_url = reverse('aurora:ide_sandbox_run')
        self.lint_url = reverse('aurora:ide_sandbox_lint')

    def test_file_tree_api_returns_json(self):
        """Verify the file tree structure returns a standard directory object."""
        response = self.client.get(self.tree_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('text', data)
        self.assertIn('type', data)

    @patch('aurora.views.ide_operations.docker.from_env')
    def test_run_code_api_sandbox_execution(self, mock_docker_env):
        """Ensure code runs in isolation and triggers the Docker SDK client safely."""
        mock_client = MagicMock()
        mock_container_output = b"Hello from the sandbox\n"
        mock_client.containers.run.return_value = mock_container_output
        mock_docker_env.return_value = mock_client

        payload = {"code": "print('Hello from the sandbox')"}
        response = self.client.post(
            self.run_url, 
            data=json.dumps(payload), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("Hello from the sandbox", response.json()['output'])
        mock_client.containers.run.assert_called_once()

    @patch('aurora.views.ide_operations.subprocess.run')
    def test_lint_code_api_clean_status(self, mock_subprocess):
        """Confirm the linter correctly parses and cleans up file path tokens."""
        mock_result = MagicMock()
        # Mocking the exact string pattern that the real view looks for to replace
        mock_result.stdout = "/tmp/fake_temp_file.py:1:1: E999 SyntaxError"
        mock_subprocess.return_value = mock_result

        with patch('aurora.views.ide_operations.tempfile.NamedTemporaryFile') as mock_temp:
            mock_file = MagicMock()
            mock_file.name = "/tmp/fake_temp_file.py"
            mock_temp.return_value.__enter__.return_value = mock_file

            payload = {"code": "invalid code logic"}
            response = self.client.post(
                self.lint_url, 
                data=json.dumps(payload), 
                content_type='application/json'
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("current_file.py", response.json()['errors'])
# ======================================================================
# END: IDE_AND_SANDBOX_INTEGRATION_TESTS (PATCH 1 OF 1)
# ======================================================================
