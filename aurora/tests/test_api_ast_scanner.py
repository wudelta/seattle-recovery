# ======================================================================
# FILE: aurora/tests/test_api_ast_scanner.py (PATCH 1 OF 1)
# START: TEST_OGM_AST_SCANNER_SUITE
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
from aurora.utils.ast_scanner import OGMTopographyScanner

class TestOGMASTDependencyScanner(TestCase):
    """Validates full relational-to-graph signal sync and AST compilation."""

    def setUp(self):
        """Prepares structural test parameters and cleanses graph state safely."""
        super().setUp()
        
        # Track every file path involved in this test execution for a clean exit sweep
        self.tracked_paths = set(["aurora/core_logic.py", "aurora/models.py", "hopehub/api/get_content_api.py"])
        
        # Enforce sandbox file tree isolation on disk using a unique directory
        self.sandbox_id = f"tmp_test_sandbox_{uuid.uuid4().hex}"
        self.test_dir = os.path.join(settings.BASE_DIR, self.sandbox_id)
        os.makedirs(os.path.join(self.test_dir, "aurora"), exist_ok=True)

        self.src_file_path = "aurora/core_logic.py"
        self.tgt_file_path = "aurora/models.py"
        self.dev_user = User.objects.create_user(username="delta_test", password="secure_lock")

        # Write out dummy scan scripts into our isolated workspace root
        with open(os.path.join(self.test_dir, self.src_file_path), "w", encoding="utf-8") as f:
            f.write("import os\nfrom aurora.models import ComponentRegistry\n")
        with open(os.path.join(self.test_dir, self.tgt_file_path), "w", encoding="utf-8") as f:
            f.write("# Stub target file\n")

        # TRANSACT-GRAPH ISOLATION ENGINE: Isolate state cleanly before running assertions
        self.flush_graph_database()

    def tearDown(self):
        """Cleans up disk structures and drops ephemeral graph entries cleanly."""
        # Dynamically append any new out-of-band paths discovered by the scanner during execution
        try:
            current_records = ComponentRegistry.objects.values_list('file_path', flat=True)
            self.tracked_paths.update(current_records)
        except Exception:
            pass

        # Wipe all records that touched our execution stream
        self.flush_graph_database()
        
        # Erase isolated temporary files safely
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

    def test_end_to_end_signal_and_ast_mapping(self):
        """Verifies PostgreSQL inserts propagate nodes, and scanner connects them."""
        target_record = ComponentRegistry.objects.create(
            file_path=self.tgt_file_path, name="Models Node", created_by=self.dev_user
        )
        source_record = ComponentRegistry.objects.create(
            file_path=self.src_file_path, name="Core Engine Node", created_by=self.dev_user
        )
        
        src_node = ComponentNode.nodes.get(file_path=self.src_file_path)
        tgt_node = ComponentNode.nodes.get(file_path=self.tgt_file_path)
        
        self.assertEqual(src_node.postgres_id, str(source_record.id))
        self.assertEqual(tgt_node.postgres_id, str(target_record.id))
        
        # Point scanner at our isolated absolute folder path location to trace connections
        scanner = OGMTopographyScanner(workspace_root=self.test_dir)
        scanner.map_workspace_topography()
        
        # Force fresh lookup from the graph layer to check updated relationships
        src_node.refresh()
        self.assertTrue(src_node.depends_on.is_connected(tgt_node))
# ======================================================================
# END: TEST_OGM_AST_SCANNER_SUITE (PATCH 1 OF 1)
# ======================================================================
