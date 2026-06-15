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
        """Establish structural mock records and clean the Neo4j loopback container."""
        neomodel_db.cypher_query("MATCH (n) DETACH DELETE n")
        
        # Provision parent component asset to establish required foreign key constraints
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username="engine_tester", password="password_abc")
        self.parent_component = ComponentRegistry.objects.create(
            file_path="app/core/minions/engine.py",
            name="minion_engine_core",
            created_by=self.user
        )
        
        # Seed a test directive row inside the database matching DeltaDirectives criteria
        self.test_directive = DeltaDirectives.objects.create(
            component_registry=self.parent_component,
            directive_name="minion_test_mock",
            instructions="You are a strict test validator. Echo the inputs.",
            constraints={"model": "llama-3.1-8b-instant", "temperature": 0.2},
            is_active=True
        )

    def tearDown(self):
        """Flush simulated graph footprint nodes to satisfy strict state isolation."""
        neomodel_db.cypher_query("MATCH (n) DETACH DELETE n")

    def test_run_minion_task_returns_graceful_error_if_minion_is_missing(self):
        """Error Check: Querying an unconfigured row token must return an explicit error string."""
        runner = MinionRunner()
        result = runner.run_minion_task("non_existent_minion", "Hello Engine")
        self.assertIn("Error: Minion configuration row", result)

    @patch('requests.post')
    def test_run_minion_task_extracts_db_rules_and_queries_groq_successfully(self, mock_post):
        """Execution Check: Verify database constraints and prompts parse down to the API request."""
        # Mock a successful standard OpenAI/Groq Chat Completions JSON output block
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

        # Instantiate the runner INSIDE the environment patch block so __init__ picks up the key
        with patch.dict('os.environ', {'MINION_CLOUD_API_KEY': 'gsk_mock_validation_key'}):
            runner = MinionRunner()
            output = runner.run_minion_task("minion_test_mock", "Execute validation track alpha")
            
        self.assertEqual(output, "Mocked validation output response string.")
        
        # Verify the outgoing payload explicitly extracted database fields correctly
        called_args, called_kwargs = mock_post.call_args
        payload_data = called_kwargs["json"]
        
        self.assertEqual(payload_data["model"], "llama-3.1-8b-instant")
        self.assertEqual(payload_data["temperature"], 0.2)
        
        # FIX: Access the tokenized message index array slices accurately to verify values
        self.assertEqual(payload_data["messages"][0]["content"], "You are a strict test validator. Echo the inputs.")
        self.assertEqual(payload_data["messages"][1]["content"], "Execute validation track alpha")
# ======================================================================
# END: MINION_ENGINE_INTEGRATION_AND_FALLBACK_TESTS (PATCH 1 OF 1)
# ======================================================================
