# ======================================================================
# FILE: aurora/tests/test_page_skeleton.py (PATCH 1 OF 4)
# START: INITIAL CONFIGURATIONS & ISOLATED SANDBOX SETUP
# ======================================================================
import os
import shutil
from django.test import TestCase
from aurora.utils.page_skeleton import PageSkeletonBuilder  # Updated path to utils package reference

class PageSkeletonBuilderTests(TestCase):
    """Test suite ensuring absolute architectural compliance for zero-token builds."""

    def setUp(self):
        """Establish a clean, isolated sandbox workspace before each test."""
        self.base_dir = os.getcwd()
        self.test_app = "test_sandbox_app"
        self.test_page = "recovery_matrix"
        self.class_name = "RecoveryMatrixView"
        
        # Build required layout subdirectories
        os.makedirs(os.path.join(self.base_dir, self.test_app, 'views'), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, self.test_app, 'templates', self.test_app), exist_ok=True)
        os.makedirs(os.path.join(self.base_dir, self.test_app, 'tests'), exist_ok=True)
        
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
# ======================================================================
# END: INITIAL CONFIGURATIONS & ISOLATED SANDBOX SETUP
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_page_skeleton.py (PATCH 2 OF 4)
# START: INPUT CLEANING, TEMPLATE EXTENSION & CLASS VIEW VALIDATION
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
        t_file = os.path.join(self.base_dir, self.test_app, 'templates', self.test_app, f'{self.test_page}.html')
        test_file = os.path.join(self.base_dir, self.test_app, 'tests', f'test_page_{self.test_page}_{self.test_app}.py')
        self.assertTrue(os.path.exists(t_file))
        # ALIGNMENT: Ensure the newly isolated page unit test file is successfully written to disk
        self.assertTrue(os.path.exists(test_file))
        with open(t_file, 'r') as f:
            content = f.read()
        self.assertIn(f'{{% extends "{self.test_app}/{self.test_app}_base.html" %}}', content)
        self.assertIn('{% block content %}', content)
        self.assertIn('href="{{ return_path }}"', content)
        self.assertIn(f'The class-based structure for <strong>{self.class_name}</strong>', content)

    def test_forge_page_step_2_class_based_view_generation(self):
        """Step 2: Assert Class View file matches Django's standard TemplateView paradigm."""
        PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        v_file = os.path.join(self.base_dir, self.test_app, 'views', f'{self.test_page}_view.py')
        self.assertTrue(os.path.exists(v_file))
        with open(v_file, 'r') as f:
            content = f.read()
        self.assertIn(f"class {self.class_name}(LoginRequiredMixin, TemplateView):", content)
        self.assertIn(f'template_name = "{self.test_app}/{self.test_page}.html"', content)
        self.assertIn('context["return_path"] = "/hopehub/" if', content)
# ======================================================================
# END: INPUT CLEANING, TEMPLATE EXTENSION & CLASS VIEW VALIDATION
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_page_skeleton.py (PATCH 3 OF 4)
# START: PACKAGE EXPORTER INJECTION & URL DISPATCH VERIFICATION
# ======================================================================
    def test_forge_page_step_3_init_package_whitelist_injection(self):
        """Step 3: Assert the view is prepended as an import and cleanly appended to __all__."""
        PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        with open(self.init_path, 'r') as f:
            content = f.read()
        # Assert the explicit relative import structure exists
        self.assertTrue(content.startswith(f"from .{self.test_page}_view import {self.class_name}\n"))
        # Assert the class symbol string is safely injected inside the exporter array
        self.assertIn(f"'{self.class_name}',", content)

    def test_forge_page_step_4_url_routing_injection(self):
        """Step 4: Assert url patterns successfully catch and configure the new View dispatch node."""
        PageSkeletonBuilder.forge_page(self.test_app, self.test_page, visibility="private")
        with open(self.urls_path, 'r') as f:
            content = f.read()
        # Assert the generated path matches Django 4.x/5.x syntax guidelines
        expected_route = f"path('{self.test_page}/', views.{self.class_name}.as_view(), name='{self.test_page}'),"
        self.assertIn(expected_route, content)
# ======================================================================
# END: PACKAGE EXPORTER INJECTION & URL DISPATCH VERIFICATION
# ======================================================================

# ======================================================================
# FILE: aurora/tests/test_page_skeleton.py (PATCH 4 OF 4)
# START: COLLISION PROTECTION & LIFECYCLE PURGE VERIFICATION
# ======================================================================
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
        v_file = os.path.join(self.base_dir, self.test_app, 'views', f'{self.test_page}_view.py')
        t_file = os.path.join(self.base_dir, self.test_app, 'templates', self.test_app, f'{self.test_page}.html')
        test_file = os.path.join(self.base_dir, self.test_app, 'tests', f'test_page_{self.test_page}_{self.test_app}.py')
        
        # Verify all physical files (including the isolated test file) are deleted from disk
        self.assertFalse(os.path.exists(v_file))
        self.assertFalse(os.path.exists(t_file))
        self.assertFalse(os.path.exists(test_file))
        
        # Verify lines are scrubbed cleanly from registrations
        with open(self.init_path, 'r') as f:
            self.assertNotIn(self.class_name, f.read())
        with open(self.urls_path, 'r') as f:
            self.assertNotIn(f"views.{self.class_name}.as_view()", f.read())
# ======================================================================
# END: COLLISION PROTECTION & LIFECYCLE PURGE VERIFICATION
# ======================================================================
