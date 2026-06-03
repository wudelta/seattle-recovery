# aurora/tests/test_api_skeleton.py
import os
import shutil
from django.test import TestCase
from aurora.api_skeleton import ApiSkeletonBuilder

class ApiSkeletonBuilderTests(TestCase):
    """Test suite ensuring absolute structural compliance for zero-token API builds."""

    def setUp(self):
        """Establish a clean, isolated sandbox workspace before each test."""
        self.base_dir = os.getcwd()
        self.test_app = "test_sandbox_app"
        self.test_endpoint = "metrics_stream"
        self.func_name = "metrics_stream_endpoint"
        
        # Build required layout subdirectories
        os.makedirs(os.path.join(self.base_dir, self.test_app, 'views'), exist_ok=True)
        
        # Initialize basic files with standard project entry configurations
        self.init_path = os.path.join(self.base_dir, self.test_app, 'views', '__init__.py')
        with open(self.init_path, 'w') as f:
            f.write("__all__ = [\n]")
            
        self.urls_path = os.path.join(self.base_dir, self.test_app, 'urls.py')
        with open(self.urls_path, 'w') as f:
            f.write("urlpatterns = [\n]")

    def tearDown(self):
        """Surgically destroy the sandbox layout to prevent workspace pollution."""
        sandbox_path = os.path.join(self.base_dir, self.test_app)
        if os.path.exists(sandbox_path):
            shutil.rmtree(sandbox_path)

    def test_clean_inputs_normalizes_case_and_characters(self):
        """Verify inputs strip invalid tokens and suffix the function identifier."""
        app, endpoint, func = ApiSkeletonBuilder.clean_inputs(" HopeHub! ", "fetch_DATA_123")
        self.assertEqual(app, "hopehub")
        self.assertEqual(endpoint, "fetch_data_123")
        self.assertEqual(func, "fetch_data_123_endpoint")

    def test_forge_api_generates_functional_view_with_json_payload(self):
        """Verify view is created, protected by auth, and delivers JsonResponse payload."""
        result = ApiSkeletonBuilder.forge_api(self.test_app, self.test_endpoint)
        self.assertEqual(result["status"], "success")
        
        v_file = os.path.join(self.base_dir, self.test_app, 'views', f'{self.test_endpoint}_view.py')
        self.assertTrue(os.path.exists(v_file))
        
        with open(v_file, 'r') as f:
            content = f.read()
            
        self.assertIn("from django.http import JsonResponse", content)
        self.assertIn("from django.contrib.auth.decorators import login_required", content)
        self.assertIn("@login_required", content)
        self.assertIn(f"def {self.func_name}(request):", content)
        self.assertIn('"status": "success"', content)

    def test_forge_api_registers_packages_and_urls_correctly(self):
        """Verify view function is appended to __init__.py and wired cleanly to urls.py."""
        ApiSkeletonBuilder.forge_api(self.test_app, self.test_endpoint)
        
        # Check __init__.py export hook
        with open(self.init_path, 'r') as f:
            init_content = f.read()
        self.assertTrue(init_content.startswith(f"from .{self.test_endpoint}_view import {self.func_name}\n"))
        self.assertIn(f"'{self.func_name}',", init_content)
        
        # Check urls.py routing rule
        with open(self.urls_path, 'r') as f:
            urls_content = f.read()
        expected_route = f"path('api/{self.test_endpoint}/', views.{self.func_name}, name='{self.func_name}'),"
        self.assertIn(expected_route, urls_content)

    def test_purge_api_removes_files_and_cleans_registrations(self):
        """Verify API structural footprints disappear entirely after a purge sequence."""
        ApiSkeletonBuilder.forge_api(self.test_app, self.test_endpoint)
        
        purge_result = ApiSkeletonBuilder.purge_api(self.test_app, self.test_endpoint)
        self.assertEqual(purge_result["status"], "success")
        
        v_file = os.path.join(self.base_dir, self.test_app, 'views', f'{self.test_endpoint}_view.py')
        self.assertFalse(os.path.exists(v_file))
        
        with open(self.init_path, 'r') as f:
            self.assertNotIn(self.func_name, f.read())
        with open(self.urls_path, 'r') as f:
            self.assertNotIn(f"views.{self.func_name}", f.read())
