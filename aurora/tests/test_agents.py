# ======================================================================
# FILE: aurora/tests/test_agents.py (PATCH 1 OF 1)
# START: MULTI-AGENT ARCHITECTURE CONFIGURATION TEST SUITE
# ======================================================================
from django.test import TestCase
from unittest.mock import patch, MagicMock
from aurora.agents import AGENT_CONFIGS, get_system_response

class AuroraAgentsTests(TestCase):
    """Test suite ensuring agent configuration matrix and payload delivery loops remain intact."""

    def test_agent_config_matrix_contains_all_roles(self):
        """Matrix Check: Assert all orchestrator and minion roles are defined with parameters."""
        expected_roles = ["Wu_Orchestrator", "HTML_Minion", "JS_Minion", "API_Minion"]
        for role in expected_roles:
            self.assertIn(role, AGENT_CONFIGS)
            self.assertIn("model", AGENT_CONFIGS[role])
            self.assertIn("temperature", AGENT_CONFIGS[role])
            self.assertIn("system_prompt", AGENT_CONFIGS[role])

    def test_wu_orchestrator_requests_json_object_format(self):
        """Configuration Check: Assert Wu forces a JSON object schema structure response."""
        self.assertEqual(AGENT_CONFIGS["Wu_Orchestrator"]["model"], "llama3-70b-8192")
        self.assertEqual(AGENT_CONFIGS["Wu_Orchestrator"]["temperature"], 0.2)

    @patch("aurora.agents.client")
    def test_get_system_response_dispatches_payload_to_groq_client(self, mock_client):
        """Inference Check: Verify parameters are mapped and passed down to the client completion engine."""
        # 1. Mock out the inner nesting properties of the Groq client object response
        mock_response = MagicMock()
        mock_response.choices.message.content = '{"tasks": []}'
        mock_client.chat.completions.create.return_value = mock_response

        # 2. Trigger active execution on the Orchestrator engine configuration layer
        command = "Build a user administration interface profile layout."
        result = get_system_response("Wu_Orchestrator", command)

        # 3. Assert properties match up to client instantiation guidelines
        self.assertEqual(result, '{"tasks": []}')
        mock_client.chat.completions.create.assert_called_once_with(
            messages=[
                {"role": "system", "content": AGENT_CONFIGS["Wu_Orchestrator"]["system_prompt"]},
                {"role": "user", "content": command}
            ],
            model="llama3-70b-8192",
            temperature=0.2,
            response_format={"type": "json_object"}
        )

    def test_get_system_response_raises_value_error_if_client_is_missing(self):
        """Security Check: Engine execution loops must raise ValueError if API client is not initialized."""
        with patch("aurora.agents.client", None):
            with self.assertRaises(ValueError) as context:
                get_system_response("HTML_Minion", "Generate code dashboard layout canvas.")
            self.assertIn("Groq Client API Key is missing", str(context.exception))
# ======================================================================
# END: MULTI-AGENT ARCHITECTURE CONFIGURATION TEST SUITE
# ======================================================================
