# ======================================================================
# FILE: aurora/tests/test_api_skeleton.py (PATCH 1 OF 2)
# START: INITIAL CONFIGURATIONS & ISOLATED SANDBOX SETUP
# ======================================================================
import os
import uuid
import shutil
from django.test import TestCase
from django.conf import settings
from neomodel import db as neomodel_db
from aurora.models import ComponentRegistry
from aurora.utils.api_skeleton import ApiSkeletonBuilder

class ApiSkeletonBuilderTests(TestCase):
    """Test suite ensuring absolute structural compliance for zero-token API builds."""

    def setUp(self):
        """Establish a clean, isolated sandbox workspace before each test."""
        super().setUp()
        
        # Unique workspace identification string mapping
        self.sandbox_suffix = uuid.uuid4().hex[:8]
        self.test_app = f"test_sandbox_app_{self.sandbox_suffix}"
        self.test_endpoint = "metrics_stream"
        self.func_name = "metrics_stream_endpoint"
        
        # Anchor sandbox roots securely to settings.BASE_DIR away from repository paths
        self.base_dir = settings.BASE_DIR
        self.test_dir = os.path.join(self.base_dir, self.test_app)
        self.tracked_paths = set()

        # TRANSACT-GRAPH ISOLATION ENGINE: Pure baseline transactional purge
        self.flush_graph_database()

        # STRUCTURAL ALIGNMENT: Build 'api' package folder explicitly inside safe workspace
        os.makedirs(os.path.join(self.test_dir, 'api'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'tests'), exist_ok=True)

        # Initialize basic files with standard project entry configurations
        self.init_path = os.path.join(self.test_dir, 'api', '__init__.py')
        with open(self.init_path, 'w', encoding='utf-8') as f:
            f.write("__all__ = [\n]")

        self.urls_path = os.path.join(self.test_dir, 'urls.py')
        with open(self.urls_path, 'w', encoding='utf-8') as f:
            f.write("urlpatterns = [\n]")

    def tearDown(self):
        """Surgically destroy the sandbox layout to prevent workspace pollution."""
        # Programmatically pull any records written via implicit backend builders or signals
        try:
            current_records = ComponentRegistry.objects.values_list('file_path', flat=True)
            self.tracked_paths.update(current_records)
        except Exception:
            pass

        self.flush_graph_database()

        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
        super().tearDown()

    def flush_graph_database(self):
        """Purges any structural graph records matching the dynamic signature tracking parameters."""
        try:
            # Query targets matching paths generated during the forge operation phase
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path CONTAINS $signature OR n.file_path IN $paths DETACH DELETE n",
                {"signature": self.test_app, "paths": list(self.tracked_paths)}
            )
        except Exception:
            pass
# ======================================================================
# END: INITIAL CONFIGURATIONS & ISOLATED SANDBOX SETUP (PATCH 1 OF 2)
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_api_skeleton.py (PATCH 2 OF 2)
# START: INPUT CLEANING, ASSET FORGING & PACKAGE PURGE ASSERTIONS
# ======================================================================
    def test_clean_inputs_normalizes_case_and_characters(self):
        """Verify inputs strip invalid tokens and suffix the function identifier."""
        app, endpoint, func = ApiSkeletonBuilder.clean_inputs(" HopeHub! ", "fetch_DATA_123")
        self.assertEqual(app, "hopehub")
        self.assertEqual(endpoint, "fetch_data_123")
        self.assertEqual(func, "fetch_data_123_endpoint")

    def test_forge_api_generates_functional_view_with_json_payload(self):
        """Verify view is created inside api/, protected by auth, and delivers JsonResponse payload."""
        # Execute forge with standard baseline visibility parameter
        result = ApiSkeletonBuilder.forge_api(self.test_app, self.test_endpoint, visibility="private")
        self.assertEqual(result["status"], "success")

        # ALIGNMENT: Target isolated api folder and verify structural existence
        api_file = os.path.join(self.test_dir, 'api', f'{self.test_endpoint}_api.py')
        test_file = os.path.join(self.test_dir, 'tests', f'test_api_{self.test_endpoint}_{self.test_app}.py')
        
        self.assertTrue(os.path.exists(api_file))
        self.assertTrue(os.path.exists(test_file))

        with open(api_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("from django.http import JsonResponse", content)
            self.assertIn("from django.contrib.auth.decorators import login_required", content)
            self.assertIn("@login_required", content)
            self.assertIn(f"def {self.func_name}(request):", content)
            self.assertIn('"status": "success"', content)

    def test_forge_api_registers_packages_and_urls_correctly(self):
        """Verify view function is appended to api/__init__.py and wired cleanly to urls.py."""
        ApiSkeletonBuilder.forge_api(self.test_app, self.test_endpoint, visibility="private")

        # Check api/__init__.py export hook
        with open(self.init_path, 'r', encoding='utf-8') as f:
            init_content = f.read()
            self.assertTrue(init_content.startswith(f"from .{self.test_endpoint}_api import {self.func_name}\n"))
            self.assertIn(f"'{self.func_name}',", init_content)

        # Check urls.py routing rule aligning with api_commands naming context
        with open(self.urls_path, 'r', encoding='utf-8') as f:
            urls_content = f.read()
            expected_route = f"path('api/{self.test_endpoint}/', api_commands.{self.func_name}, name='{self.func_name}'),"
            self.assertIn(expected_route, urls_content)

    def test_purge_api_removes_files_and_cleans_registrations(self):
        """Verify API structural footprints disappear entirely after an isolated purge sequence."""
        ApiSkeletonBuilder.forge_api(self.test_app, self.test_endpoint, visibility="private")
        purge_result = ApiSkeletonBuilder.purge_api(self.test_app, self.test_endpoint)
        self.assertEqual(purge_result["status"], "success")

        # Verify physical code files are safely stripped
        api_file = os.path.join(self.test_dir, 'api', f'{self.test_endpoint}_api.py')
        test_file = os.path.join(self.test_dir, 'tests', f'test_api_{self.test_endpoint}_{self.test_app}.py')
        
        self.assertFalse(os.path.exists(api_file))
        self.assertFalse(os.path.exists(test_file))

        # Confirm whitelists and routings clean up beautifully
        with open(self.init_path, 'r', encoding='utf-8') as f:
            self.assertNotIn(self.func_name, f.read())
        with open(self.urls_path, 'r', encoding='utf-8') as f:
            self.assertNotIn(f"api_commands.{self.func_name}", f.read())
# ======================================================================
# END: PACKAGE ROUTING INJECTIONS & REFACTOR-SAFE PURGE VERIFICATION (PATCH 2 OF 2)
# ======================================================================
