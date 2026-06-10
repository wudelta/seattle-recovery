# ======================================================================
# FILE: tests/test_api_ast_scanner.py (PATCH 1 OF 1)
# START: TEST_OGM_AST_SCANNER_SUITE
# ======================================================================
import os
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel import db
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode
from aurora.utils.ast_scanner import OGMTopographyScanner

class TestOGMASTDependencyScanner(TestCase):
    """Validates full relational-to-graph signal sync and AST compilation."""

    def setUp(self):
        """Prepares structural test parameters and cleanses graph state."""
        # Constraint C: Complete Cypher Flush Loop via neomodel raw execution
        db.cypher_query("MATCH (n) DETACH DELETE n")

        # Create authenticated developer shell to satisfy PostgreSQL PROTECT FK constraint
        self.dev_user = User.objects.create_user(username="delta_test", password="secure_lock")

        # Define tracking variables for physical temp assets
        self.test_dir = "test_workspace_sandbox"
        os.makedirs(self.test_dir, exist_ok=True)

        self.src_file_path = "aurora/core_logic.py"
        self.tgt_file_path = "aurora/models.py"

        # Create physical workspace file assets mirroring standard modules
        os.makedirs(os.path.join(self.test_dir, "aurora"), exist_ok=True)
        
        with open(os.path.join(self.test_dir, self.src_file_path), "w", encoding="utf-8") as f:
            f.write("import os\nfrom aurora.models import ComponentRegistry\n")
            
        with open(os.path.join(self.test_dir, self.tgt_file_path), "w", encoding="utf-8") as f:
            f.write("# Stub target file\n")

    def tearDown(self):
        """Cleans up disk structures and drops ephemeral graph entries."""
        # Flush graph state to prevent deadlocks and leaks across test sequences
        db.cypher_query("MATCH (n) DETACH DELETE n")

        # Wipe local file structures cleanly
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_dir)

    def test_end_to_end_signal_and_ast_mapping(self):
        """Verifies PostgreSQL inserts propagate nodes, and scanner connects them."""
        # Step 1: Create PostgreSQL Records (Triggers aurora/signals.py)
        target_record = ComponentRegistry.objects.create(
            file_path=self.tgt_file_path,
            name="Models Node",
            created_by=self.dev_user
        )
        source_record = ComponentRegistry.objects.create(
            file_path=self.src_file_path,
            name="Core Engine Node",
            created_by=self.dev_user
        )

        # Confirm signals populated graph nodes autonomously into Neo4j
        src_node = ComponentNode.nodes.get(file_path=self.src_file_path)
        tgt_node = ComponentNode.nodes.get(file_path=self.tgt_file_path)
        self.assertEqual(src_node.postgres_id, str(source_record.id))
        self.assertEqual(tgt_node.postgres_id, str(target_record.id))

        # Step 2: Initialize Scanner and execute static link projection
        scanner = OGMTopographyScanner(workspace_root=self.test_dir)
        scanner.map_workspace_topography()

        # Step 3: Verify the DEPENDS_ON relationship was generated successfully
        self.assertTrue(src_node.depends_on.is_connected(tgt_node))
# ======================================================================
# END: TEST_OGM_AST_SCANNER_SUITE
# ======================================================================
