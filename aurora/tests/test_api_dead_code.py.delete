# ======================================================================
# FILE: aurora/tests/test_api_dead_code.py (PATCH 1 OF 1)
# START: COMPLETE_TEST_DEAD_CODE_ISOLATOR_SUITE
# ======================================================================
import os
import uuid
import shutil
from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from neomodel import db
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode
from aurora.utils.dead_code_isolator import DeadCodeIsolator

class TestDeadCodeIsolator(TestCase):
    """Validates the isolation engine and checks the manual locked override flag."""

    def setUp(self):
        """Cleans database graph state and establishes test assets."""
        super().setUp()
        
        # Track every file path involved in this test execution for a clean parametric sweep
        self.orphan_file = "orphan_module.py"
        self.locked_file = "locked_module.py"
        self.tracked_paths = set([self.orphan_file, self.locked_file])

        # TRANSACT-GRAPH ISOLATION ENGINE: Flush matching target nodes before running
        self.flush_graph_database()

        # Create developer profile to bypass database constraints
        self.dev_user = User.objects.create_user(username=f"isolator_test_{uuid.uuid4().hex[:6]}", password="lock")
        
        # Enforce sandbox file tree isolation on disk using a unique directory path
        self.sandbox_id = f"tmp_dead_code_sandbox_{uuid.uuid4().hex}"
        self.test_dir = os.path.join(settings.BASE_DIR, self.sandbox_id)
        os.makedirs(self.test_dir, exist_ok=True)

        # Create physical blank python components inside our unique workspace path
        with open(os.path.join(self.test_dir, self.orphan_file), "w", encoding="utf-8") as f:
            f.write("# Unlocked orphan file\n")
        with open(os.path.join(self.test_dir, self.locked_file), "w", encoding="utf-8") as f:
            f.write("# Locked orphan file\n")

    def tearDown(self):
        """Wipes physical structures and drops transient nodes from graph matrix."""
        # Dynamically append any new out-of-band paths discovered by the isolator during execution
        try:
            current_records = ComponentRegistry.objects.values_list('file_path', flat=True)
            self.tracked_paths.update(current_records)
        except Exception:
            pass

        # Wipe all graph node matches that touched our execution stream safely
        self.flush_graph_database()

        # Erase isolated temporary workspace files safely
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
        super().tearDown()

    def flush_graph_database(self):
        """Executes a scoped deletion loopback matching all tracked test data elements."""
        try:
            db.cypher_query(
                "MATCH (n) WHERE n.file_path IN $paths DETACH DELETE n",
                {"paths": list(self.tracked_paths)}
            )
        except Exception:
            pass

    def test_isolation_workflow_respects_and_skips_locked_assets(self):
        """Verifies unlocked orphans are quarantined while locked records are untouched."""
        # 1. Store records inside PostgreSQL (triggers signals to draw graph bubbles)
        unlocked_record = ComponentRegistry.objects.create(
            file_path=self.orphan_file, name="Unlocked Target", locked=False, created_by=self.dev_user
        )
        locked_record = ComponentRegistry.objects.create(
            file_path=self.locked_file, name="Locked Target", locked=True, created_by=self.dev_user
        )

        # Confirm graph entries were projected correctly via neomodel evaluation checks
        self.assertTrue(len(ComponentNode.nodes.filter(postgres_id=str(unlocked_record.id))) > 0)
        self.assertTrue(len(ComponentNode.nodes.filter(postgres_id=str(locked_record.id))) > 0)

        # 2. Execute audit scan pass inside isolated sandbox
        isolator = DeadCodeIsolator(workspace_root=self.test_dir)
        report = isolator.execute_complete_audit()

        # 3. Check reports and database statuses
        self.assertIn(self.orphan_file, report["quarantined_files"])
        self.assertIn(self.locked_file, report["skipped_locked_files"])

        # Check PostgreSQL state modification checks
        unlocked_record.refresh_from_db()
        locked_record.refresh_from_db()
        self.assertEqual(unlocked_record.status, "STAGED_FOR_DELETION")
        self.assertEqual(locked_record.status, "ACTIVE")
# ======================================================================
# END: COMPLETE_TEST_DEAD_CODE_ISOLATOR_SUITE
# ======================================================================
