# ======================================================================
# FILE: aurora/tests/test_api_dead_code.py (PATCH 1 OF 1)
# START: COMPLETE_TEST_DEAD_CODE_ISOLATOR_SUITE
# ======================================================================
import os
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel import db
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode
from aurora.utils.dead_code_isolator import DeadCodeIsolator

class TestDeadCodeIsolator(TestCase):
    """Validates the isolation engine and checks the manual locked override flag."""

    def setUp(self):
        """Cleans database graph state and establishes test assets."""
        # Constraint C: Complete Cypher Flush Loop
        db.cypher_query("MATCH (n) DETACH DELETE n")

        # Create developer profile to bypass database constraints
        self.dev_user = User.objects.create_user(username="delta_isolator_test", password="lock")

        # Set up physical layout directories
        self.test_dir = "test_dead_code_sandbox"
        os.makedirs(self.test_dir, exist_ok=True)

        self.orphan_file = "orphan_module.py"
        self.locked_file = "locked_module.py"

        # Create physical blank python components to scan
        with open(os.path.join(self.test_dir, self.orphan_file), "w", encoding="utf-8") as f:
            f.write("# Unlocked orphan file\n")
            
        with open(os.path.join(self.test_dir, self.locked_file), "w", encoding="utf-8") as f:
            f.write("# Locked orphan file\n")

    def tearDown(self):
        """Wipes physical structures and drops transient nodes from graph matrix."""
        db.cypher_query("MATCH (n) DETACH DELETE n")

        if os.path.exists(os.path.join(self.test_dir, self.orphan_file)):
            os.remove(os.path.join(self.test_dir, self.orphan_file))
        if os.path.exists(os.path.join(self.test_dir, self.locked_file)):
            os.remove(os.path.join(self.test_dir, self.locked_file))
        os.rmdir(self.test_dir)

    def test_isolation_workflow_respects_and_skips_locked_assets(self):
        """Verifies unlocked orphans are quarantined while locked records are untouched."""
        # 1. Store records inside PostgreSQL (triggers signals to draw graph bubbles)
        unlocked_record = ComponentRegistry.objects.create(
            file_path=self.orphan_file,
            name="Unlocked Target",
            locked=False,
            created_by=self.dev_user
        )
        
        locked_record = ComponentRegistry.objects.create(
            file_path=self.locked_file,
            name="Locked Target",
            locked=True,
            created_by=self.dev_user
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
