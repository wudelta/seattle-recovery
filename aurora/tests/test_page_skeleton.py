# ======================================================================
# FILE: aurora/tests/test_page_skeleton.py (PATCH 1 OF 2)
# START: INITIAL CONFIGURATIONS & ISOLATED SANDBOX SETUP
# ======================================================================
import os
import uuid
import shutil
from django.test import TestCase
from django.conf import settings
from neomodel import db as neomodel_db
from aurora.models import ComponentRegistry
from aurora.utils.page_skeleton import PageSkeletonBuilder

class PageSkeletonBuilderTests(TestCase):
    """Test suite ensuring absolute architectural compliance for zero-token builds."""

    def setUp(self):
        """Establish a clean, isolated sandbox workspace before each test."""
        super().setUp()
        
        # Unique workspace identification token tracking configuration
        self.sandbox_suffix = uuid.uuid4().hex[:8]
        self.test_app = f"test_sandbox_app_{self.sandbox_suffix}"
        self.test_page = "recovery_matrix"
        self.class_name = "RecoveryMatrixView"
        
        # Secure all operations inside settings.BASE_DIR away from local workspace path trees
        self.base_dir = settings.BASE_DIR
        self.test_dir = os.path.join(self.base_dir, self.test_app)
        self.tracked_paths = set()

        # TRANSACT-GRAPH ISOLATION ENGINE: Pure transactional baseline sweep
        self.flush_graph_database()

        # Build required layout subdirectories safely inside the UUID sandbox directory
        os.makedirs(os.path.join(self.test_dir, 'views'), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'templates', self.test_app), exist_ok=True)
        os.makedirs(os.path.join(self.test_dir, 'tests'), exist_ok=True)

        # Initialize basic files with standard project entry configurations
        self.init_path = os.path.join(self.test_dir, 'views', '__init__.py')
        with open(self.init_path, 'w', encoding='utf-8') as f:
            f.write("__all__ = [\n]")

        self.urls_path = os.path.join(self.test_dir, 'urls.py')
        with open(self.urls_path, 'w', encoding='utf-8') as f:
            f.write("urlpatterns = [\n]")

    def tearDown(self):
        """Surgically destroy the sandbox layout to prevent workspace pollution."""
        # Dynamic extraction lookup from postgres to sweep graph nodes forged out-of-band
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
# FILE: aurora/tests/test_page_skeleton.py (PATCH 2 OF 2)
# START: INPUT CLEANING, ASSET FORGING & PACKAGE PURGE ASSERTIONS
# ======================================================================
    def test_clean_inputs_normalizes_case_and_characters(self):
        """Verify inputs strip invalid tokens and title case the class identifier."""
        app, page, cls = PageSkeletonBuilder.clean_inputs(" HopeHub! ", "user_profile_123")
        self.assertEqual(app, "hopehub")
        self.assertEqual(page, "user_profile_123")
        self.assertEqual(cls, "UserProfile123View")

    def test_forge_page_step_1_html_template_generation(self):
        """Step 1: Assert HTML file exists and strictly extends the app base layout."""
        result = PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        self.assertEqual(result["status"], "success")
        
        t_file = os.path.join(self.test_dir, 'templates', self.test_app, f'{self.test_page}.html')
        test_file = os.path.join(self.test_dir, 'tests', f'test_page_{self.test_page}_{self.test_app}.py')
        
        self.assertTrue(os.path.exists(t_file))
        self.assertTrue(os.path.exists(test_file))
        
        with open(t_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(f'{{% extends "{self.test_app}/{self.test_app}_base.html" %}}', content)
            self.assertIn('{% block content %}', content)
            self.assertIn('href="{{ return_path }}"', content)
            self.assertIn(f'The class-based structure for <strong>{self.class_name}</strong>', content)

    def test_forge_page_step_2_class_based_view_generation(self):
        """Step 2: Assert Class View file matches Django's standard TemplateView paradigm."""
        PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        v_file = os.path.join(self.test_dir, 'views', f'{self.test_page}_view.py')
        self.assertTrue(os.path.exists(v_file))
        
        with open(v_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn(f"class {self.class_name}(LoginRequiredMixin, TemplateView):", content)
            self.assertIn(f'template_name = "{self.test_app}/{self.test_page}.html"', content)
            self.assertIn('context["return_path"] = "/hopehub/" if', content)

    def test_forge_page_step_3_init_package_whitelist_injection(self):
        """Step 3: Assert the view is prepended as an import and cleanly appended to __all__."""
        PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        with open(self.init_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertTrue(content.startswith(f"from .{self.test_page}_view import {self.class_name}\n"))
            self.assertIn(f"'{self.class_name}',", content)

    def test_forge_page_step_4_url_routing_injection(self):
        """Step 4: Assert url patterns successfully catch and configure the new View dispatch node."""
        PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        with open(self.urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
            expected_route = f"path('{self.test_page}/', views.{self.class_name}.as_view(), name='{self.test_page}'),"
            self.assertIn(expected_route, content)

    def test_forge_page_prevents_collision_overwrites(self):
        """Collision Check: Verify forge operations abort safely if target elements are active."""
        PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        collision_result = PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        self.assertEqual(collision_result["status"], "error")
        self.assertIn("Collision: Component", collision_result["message"])

    def test_purge_page_removes_files_and_cleans_registrations(self):
        """Purge Integrity: Verify structural traces vanish from files completely on teardown."""
        PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        purge_result = PageSkeletonBuilder.purge_page(self.test_app, self.test_page)
        self.assertEqual(purge_result["status"], "success")
        
        v_file = os.path.join(self.test_dir, 'views', f'{self.test_page}_view.py')
        t_file = os.path.join(self.test_dir, 'templates', self.test_app, f'{self.test_page}.html')
        test_file = os.path.join(self.test_dir, 'tests', f'test_page_{self.test_page}_{self.test_app}.py')
        
        self.assertFalse(os.path.exists(v_file))
        self.assertFalse(os.path.exists(t_file))
        self.assertFalse(os.path.exists(test_file))
        
        with open(self.init_path, 'r', encoding='utf-8') as f:
            self.assertNotIn(self.class_name, f.read())
        with open(self.urls_path, 'r', encoding='utf-8') as f:
            self.assertNotIn(f"views.{self.class_name}.as_view()", f.read())
# ======================================================================
# END: COLLISION PROTECTION & LIFECYCLE PURGE VERIFICATION (PATCH 2 OF 2)
# ======================================================================
