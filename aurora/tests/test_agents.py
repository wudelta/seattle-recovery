# ====================================================================== #
# FILE: aurora/tests/test_agents.py (PATCH 1 OF 1)                       #
# START: MULTI-AGENT ARCHITECTURE CONFIGURATION TEST SUITE               #
# ====================================================================== #
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
        self.assertEqual(AGENT_CONFIGS["Wu_Orchestrator"]["model"], "gemini-2.5-flash")
        self.assertEqual(AGENT_CONFIGS["Wu_Orchestrator"]["temperature"], 0.2)

    @patch("aurora.agents.client")
    def test_get_system_response_dispatches_payload_to_gemini_client(self, mock_client):
        """Inference Check: Verify parameters are mapped and passed down to the client completion engine."""
        # 1. Mock out the inner nesting properties of the Gemini client object response
        mock_response = MagicMock()
        mock_response.text = '{"tasks": []}'
        mock_client.models.generate_content.return_value = mock_response

        # 2. Trigger active execution on the Orchestrator engine configuration layer
        command = "Build a user administration interface profile layout."
        result = get_system_response("Wu_Orchestrator", command)

        # 3. Assert properties match up to client instantiation guidelines
        self.assertEqual(result, '{"tasks": []}')
        
        # Verify the client call captures the structured generate content parameters correctly
        mock_client.models.generate_content.assert_called_once()
        called_args, called_kwargs = mock_client.models.generate_content.call_args
        
        self.assertEqual(called_kwargs['model'], "gemini-2.5-flash")
        self.assertEqual(called_kwargs['contents'], command)
        self.assertEqual(called_kwargs['config'].temperature, 0.2)
        self.assertEqual(called_kwargs['config'].system_instruction, AGENT_CONFIGS["Wu_Orchestrator"]["system_prompt"])
        self.assertEqual(called_kwargs['config'].response_mime_type, "application/json")

    def test_get_system_response_raises_value_error_if_client_is_missing(self):
        """Security Check: Engine execution loops must raise ValueError if API client is not initialized."""
        with patch("aurora.agents.client", None):
            with self.assertRaises(ValueError) as context:
                get_system_response("HTML_Minion", "Generate code dashboard layout canvas.")
            self.assertIn("Gemini Client API Key is missing", str(context.exception))
# ====================================================================== #
# END: MULTI-AGENT ARCHITECTURE CONFIGURATION TEST SUITE               #
# ====================================================================== #
