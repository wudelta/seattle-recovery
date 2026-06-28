# ======================================================================
# FILE: aurora/tests/test_minion_engine.py (PATCH 1 OF 1)
# START: MINION_ENGINE_INTEGRATION_AND_FALLBACK_TESTS
# ======================================================================
from django.test import TestCase
from unittest.mock import patch, AsyncMock, MagicMock
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
        # FIX: Updated substring assertion to match the actual exception prefix formatting in engine.py
        self.assertIn("[REGISTRY ERROR]: Minion configuration", result)

    @patch('groq.resources.chat.completions.AsyncCompletions.create')
    def test_run_minion_task_extracts_db_rules_and_queries_groq_successfully(self, mock_create):
        """Execution Check: Verify database constraints and prompts parse down to the SDK request."""
        
        # Build an async generator mock to simulate the official SDK stream chunks
        async def mock_stream_generator(*args, **kwargs):
            # Create a mock chunk simulating the Groq SDK's chunk topology
            mock_chunk = MagicMock()
            mock_chunk.choices = [MagicMock()]
            mock_chunk.choices[0].delta.content = "Mocked validation output response string."
            yield mock_chunk

        mock_create.side_effect = mock_stream_generator

        with patch.dict('os.environ', {'GROQ_API_KEY': 'gsk_mock_validation_key'}):
            runner = MinionRunner()
            output = runner.run_minion_task("minion_test_mock", "Execute validation track alpha")
            
            # Assert stitched string response matches mock expectation
            self.assertEqual(output, "Mocked validation output response string.")

        # Extract arguments passed directly to the client SDK create method
        called_kwargs = mock_create.call_args.kwargs
        self.assertEqual(called_kwargs["model"], "llama-3.1-8b-instant")
        self.assertEqual(called_kwargs["temperature"], 0.2)
        self.assertEqual(called_kwargs["messages"][0]["content"], "You are a strict test validator. Echo the inputs.")
        self.assertEqual(called_kwargs["messages"][1]["content"], "Execute validation track alpha")

# ======================================================================
# END: MINION_ENGINE_INTEGRATION_AND_FALLBACK_TESTS (PATCH 1 OF 1)
# ======================================================================
