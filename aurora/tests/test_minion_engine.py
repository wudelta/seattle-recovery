# ======================================================================
# FILE: aurora/tests/test_minion_engine.py (PATCH 1 OF 1)
# START: MINION_ENGINE_INTEGRATION_AND_FALLBACK_TESTS
# ======================================================================
from django.test import TestCase
from unittest.mock import patch, MagicMock
from neomodel import db as neomodel_db
from aurora.models import ComponentRegistry, DeltaDirectives
from aurora.minions.engine import MinionRunner

class MinionEngineExecutionTests(TestCase):
    """Twin-Track verification suite validating the data-driven Groq engine."""

    def setUp(self):
        """Establish structural mock records and clean the Neo4j loopback container safely."""
        # SAFE GRAPH FIX: Restrict flush strictly to sandboxed paths to protect production data
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'app/core/minions/' DETACH DELETE n"
            )
        except Exception:
            pass

        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username="engine_tester", password="password_abc")
        
        self.parent_component = ComponentRegistry.objects.create(
            file_path="app/core/minions/engine.py",
            name="minion_engine_core",
            created_by=self.user
        )

        # FIXED: Bound created_by tracking link to satisfy non-null column constraint updates
        self.test_directive = DeltaDirectives.objects.create(
            directive_name="minion_test_mock",
            instructions="You are a strict test validator. Echo the inputs.",
            constraints={"model": "llama-3.1-8b-instant", "temperature": 0.2},
            is_active=True,
            created_by=self.user
        )

    def tearDown(self):
        """Flush simulated graph footprint nodes to satisfy strict state isolation."""
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'app/core/minions/' DETACH DELETE n"
            )
        except Exception:
            pass

    def test_run_minion_task_returns_graceful_error_if_minion_is_missing(self):
        """Error Check: Querying an unconfigured row token must return an explicit error string."""
        runner = MinionRunner()
        result = runner.run_minion_task("non_existent_minion", "Hello Engine")
        self.assertIn("Error: Minion configuration row", result)

    @patch('requests.post')
    def test_run_minion_task_extracts_db_rules_and_queries_groq_successfully(self, mock_post):
        """Execution Check: Verify database constraints and prompts parse down to the API request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Mocked validation output response string."
                    }
                }
            ]
        }
        mock_post.return_value = mock_response

        with patch.dict('os.environ', {'MINION_CLOUD_API_KEY': 'gsk_mock_validation_key'}):
            runner = MinionRunner()
            output = runner.run_minion_task("minion_test_mock", "Execute validation track alpha")
            self.assertEqual(output, "Mocked validation output response string.")

        called_args, called_kwargs = mock_post.call_args
        payload_data = called_kwargs["json"]
        self.assertEqual(payload_data["model"], "llama-3.1-8b-instant")
        self.assertEqual(payload_data["temperature"], 0.2)
        self.assertEqual(payload_data["messages"][0]["content"], "You are a strict test validator. Echo the inputs.")
        self.assertEqual(payload_data["messages"][1]["content"], "Execute validation track alpha")
# ======================================================================
# END: MINION_ENGINE_INTEGRATION_AND_FALLBACK_TESTS (PATCH 1 OF 1)
# ======================================================================
