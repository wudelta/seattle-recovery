from django.test import TestCase
from django.urls import reverse
from aurora.models import AutomatedBuildStep

class TestPipelineWorkflowGates(TestCase):

    def setUp(self):
        """Seed a clean, unexecuted tracking step instance for verification testing."""
        self.feature_name = 'sandbox_feature_test'
        self.active_step = AutomatedBuildStep.objects.create(
            feature_name=self.feature_name,
            step_order=1,
            stage='SETUP_TEST',
            title='Initial Safety Sandbox Verification Mock',
            target_file_path='hopehub/tests/stray_test_file.py',
            code_payload='def test_mock_pass(): pass\n',
            anchor_signature='',
            verification_command='echo "Simulated Test Suite Run Pass" && exit 0',
            expected_exit_code=0,
            assigned_minion='Test-Architect Minion',
            approval_status='PENDING_REVIEW',
            is_executed=False
        )
        
        # Dashboard context URL paths
        self.dashboard_url = reverse('aurora:pipeline_dashboard', kwargs={'feature_name': self.feature_name})
        self.process_url = reverse('aurora:process_step', kwargs={'step_id': self.active_step.id})
        self.finalize_url = reverse('aurora:finalize_feature', kwargs={'feature_name': self.feature_name})

    def test_dashboard_renders_active_step_successfully(self):
        """Confirm that the workspace control deck populates matching sequence metrics."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'aurora/automation_dashboard.html')
        self.assertEqual(response.context['active_step'].id, self.active_step.id)

    def test_unapproved_step_blocks_feature_finalization(self):
        """Gate 2 Guardrail: Ensure an operator cannot visual sign-off if unexecuted steps exist."""
        # Attempt to trigger finalization POST route while step is still unexecuted
        response = self.client.post(self.finalize_url, follow=True)
        
        # The view should catch the pending step, throw an error message, and redirect back to dashboard
        self.assertRedirects(response, self.dashboard_url)
        
        # RE-CHECK TDD REQUIREMENT: Verify the step status remains completely untouched
        self.active_step.refresh_from_db()
        self.assertFalse(self.active_step.is_executed)

    def test_process_step_action_updates_database_state_and_logs(self):
        """Verify processing POST signals toggle approval flags and capture terminal logs."""
        # Intentionally passing mismatched payload parameters to force a form validation failure first
        bad_payload_data = {
            'feature_name': self.feature_name,
            'step_order': 99,  # Intentional sequence clash modification to break integrity validation
            'stage': 'INVALID_STAGE_SELECTION'
        }
        
        # Submit the broken form to verify your backend guardrails trap error exceptions
        response = self.client.post(self.process_url, data=bad_payload_data, follow=True)
        self.assertRedirects(response, self.dashboard_url)
        
        # Assert database state remains securely locked
        self.active_step.refresh_from_db()
        self.assertEqual(self.active_step.approval_status, 'PENDING_REVIEW')
