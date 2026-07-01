# ====================================================================== #
# FILE: aurora/tests/test_minion_engine.py (PATCH 1 OF 1)                 #
# START: MINION_ENGINE_INTEGRATION_AND_FALLBACK_TESTS                    #
# ====================================================================== #
from django.test import TestCase
from unittest.mock import patch, AsyncMock, MagicMock
from neomodel import db as neomodel_db
from aurora.models import ComponentRegistry, DeltaDirectives
from aurora.minions.engine import MinionRunner

class MinionEngineExecutionTests(TestCase):
    """Twin-Track verification suite validating the data-driven Gemini engine."""

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
            constraints={"model": "gemini-2.5-flash", "temperature": 0.2}, # UPDATED: Pointing to Gemini model targets
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

    @patch('google.genai.client.AsyncClient.Models.generate_content_stream')
    def test_run_minion_task_extracts_db_rules_and_queries_gemini_successfully(self, mock_generate_content_stream):
        """Execution Check: Verify database constraints and prompts parse down to the SDK request."""
        # Build an async generator mock to simulate the official SDK stream chunks
        async def mock_stream_generator(*args, **kwargs):
            # Create a mock chunk simulating the Google GenAI SDK's chunk topology
            mock_chunk = MagicMock()
            mock_chunk.text = "Mocked validation output response string."
            mock_chunk.usage_metadata = MagicMock()
            mock_chunk.usage_metadata.total_token_count = 50
            yield mock_chunk

        mock_generate_content_stream.side_effect = mock_stream_generator

        with patch.dict('os.environ', {'GEMINI_API_KEY': 'gen-lang-client-mock-validation-key'}):
            runner = MinionRunner()
            output = runner.run_minion_task("minion_test_mock", "Execute validation track alpha")

            # Assert stitched string response matches mock expectation
            self.assertEqual(output, "Mocked validation output response string.")

            # Extract arguments passed directly to the client SDK stream generator method
            called_kwargs = mock_generate_content_stream.call_args.kwargs
            self.assertEqual(called_kwargs["model"], "gemini-2.5-flash")
            self.assertEqual(called_kwargs["user_prompt"], "Execute validation track alpha")
            self.assertEqual(called_kwargs["config"].temperature, 0.2)
            self.assertEqual(called_kwargs["config"].system_instruction, "You are a strict test validator. Echo the inputs.")
# ====================================================================== #
# END: MINION_ENGINE_INTEGRATION_AND_FALLBACK_TESTS (PATCH 1 OF 1)        #
# ====================================================================== #
