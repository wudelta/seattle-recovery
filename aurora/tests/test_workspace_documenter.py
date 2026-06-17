# ======================================================================
# FILE: aurora/tests/test_workspace_documenter.py (PATCH 1 OF 1)
# START: WORKSPACE_CRAWLER_DOCUMENTER_INTEGRATION_TESTS
# ======================================================================
from django.test import TestCase
from unittest.mock import patch, mock_open
from neomodel import db as neomodel_db
from aurora.models import ComponentRegistry, DeltaDirectives
from aurora.utils.documenter import WorkspaceDocumenter

class WorkspaceDocumenterTests(TestCase):
    """Twin-Track verification suite validating the automated documentation crawler."""

    def setUp(self):
        """Establish baseline configuration parameters and clear sandbox graph references safely."""
        # SAFE GRAPH FIX: Restrict flush strictly to sandboxed paths to protect production data
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'aurora/' DETACH DELETE n"
            )
        except Exception:
            pass

        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username="crawler_dev", password="password_123")
        
        # 1. Establish Parent Registry Mock Asset Profile
        self.component = ComponentRegistry.objects.create(
            file_path="aurora/core_logic.py",
            name="core_logic",
            persona="COMPILER_MODULE",
            status="ACTIVE",
            created_by=self.user,
            description_audiences={}
        )
        
        # 2. Seed the required active data-driven writer minion directive configuration row
        # FIXED: Removed deprecated component_registry keyword to match standalone schema updates
        self.writer_directive = DeltaDirectives.objects.create(
            directive_name="minion_AI_writer",
            instructions="Rewrite text professionally.",
            constraints={"model": "llama-3.1-8b-instant", "temperature": 0.2},
            is_active=True
        )
        
        # Patch the environment variable required by the underlying MinionRunner constructor
        self.env_patcher = patch.dict('os.environ', {'MINION_CLOUD_API_KEY': 'gsk_mock_crawler_key'})
        self.env_patcher.start()
        self.documenter = WorkspaceDocumenter()

    def tearDown(self):
        """Flush simulated graph footprint nodes to satisfy strict state isolation loop bounds."""
        self.env_patcher.stop()
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'aurora/' DETACH DELETE n"
            )
        except Exception:
            pass

    def test_read_source_code_returns_blank_string_if_file_missing(self):
        """File Check: Requesting an unmapped file path must exit cleanly without halting execution."""
        result = self.documenter.read_source_code("non_existent_file_path.py")
        self.assertEqual(result, "")

    @patch('builtins.open', new_callable=mock_open, read_data="def handle_execution(): return True")
    @patch('os.path.exists', return_value=True)
    @patch('aurora.minions.engine.MinionRunner.query_groq_llm')
    def test_documentation_sweep_queries_engine_and_saves_audience_blocks(self, mock_query, mock_exists, mock_file):
        """Workflow Check: Verify crawling loop processes files and updates PostgreSQL field dictionaries."""
        mock_query.side_effect = [
            "Mocked detailed developer systems logic overview.",
            "Mocked clean stakeholder business translation overview."
        ]
        report = self.documenter.execute_documentation_sweep()
        
        self.assertIn("aurora/core_logic.py", report["processed_files"])
        self.assertEqual(len(report["failures"]), 0)
        
        self.component.refresh_from_db()
        self.assertEqual(
            self.component.description_audiences.get("developer_docs"),
            "Mocked detailed developer systems logic overview."
        )
        self.assertEqual(
            self.component.description_audiences.get("stakeholder_docs"),
            "Mocked clean stakeholder business translation overview."
        )

    @patch('aurora.utils.documenter.WorkspaceDocumenter.read_source_code', return_value="import os")
    def test_documentation_sweep_skips_fully_documented_components(self, mock_read):
        """Optimization Check: Assets with pre-existing dual tracking text must bypass API processing requests."""
        self.component.description_audiences = {
            "developer_docs": "Existing dev logs text data.",
            "stakeholder_docs": "Existing business logs overview text."
        }
        self.component.save()
        report = self.documenter.execute_documentation_sweep()
        self.assertIn("aurora/core_logic.py", report["skipped_files"])
        self.assertEqual(len(report["processed_files"]), 0)
# ======================================================================
# END: WORKSPACE_CRAWLER_DOCUMENTER_INTEGRATION_TESTS (PATCH 1 OF 1)
# ======================================================================
