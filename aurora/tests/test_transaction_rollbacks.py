# ======================================================================
# FILE: aurora/tests/test_transaction_rollbacks.py (PATCH 1 OF 1)
# START: TRANSACTION_APPROVALS_AND_ROLLBACK_TEST_SUITE
# ======================================================================
import json
import os
import pytest
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client  # Synchronous test client
from neomodel import db as neomodel_db
from aurora.models import WorkspaceTransaction, TrackedCommand

User = get_user_model()

@pytest.mark.django_db(transaction=True)
class TestTransactionRollbacks:
    """Twin-Track verification suite validating human-in-the-loop file creation gates."""

    def setUp(self):
        """Isolate tandem graph states strictly to avoid race conditions over local container ports."""
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'aurora/' DETACH DELETE n"
            )
        except Exception:
            pass

        # Create a sandboxed mock template file path string to track mutation impact
        self.base_dir = getattr(settings, "BASE_DIR", os.getcwd())
        self.sandbox_file_rel = "aurora/templates/aurora/pages/test_sandbox_page.html"
        self.sandbox_file_abs = os.path.join(self.base_dir, self.sandbox_file_rel)
        
        # Ensure cleanup of any leftover artifacts before test initialization
        if os.path.exists(self.sandbox_file_abs):
            os.remove(self.sandbox_file_abs)

    def tearDown(self):
        """Flush simulated graph footprints and clear file space to enforce total state isolation."""
        try:
            neomodel_db.cypher_query(
                "MATCH (n) WHERE n.file_path STARTS WITH 'aurora/' DETACH DELETE n"
            )
        except Exception:
            pass
            
        if os.path.exists(self.sandbox_file_abs):
            os.remove(self.sandbox_file_abs)

    def test_transaction_destroy_surgically_removes_affected_files(self):
        """Rollback Check: Invoking DESTROY must purge files on disk and update row records."""
        self.setUp()
        
        # Use a standard synchronous test client to remove all async loop overhead
        client = Client()

        user = User.objects.create_user(username="rollback_tester", password="secure_pass_123")
        client.force_login(user)
        
        # Setup a pending transaction tracking instance model
        tx = WorkspaceTransaction.objects.create(
            user=user,
            prompt_context="Generate a sandbox workspace testing layout context.",
            status='PENDING'
        )
        
        # Map a /page command row tracking token targeting our predicted path
        TrackedCommand.objects.create(
            transaction=tx,
            macro="/page",
            arguments=["test_sandbox_page"],
            affected_files=[self.sandbox_file_rel],
            execution_order=0
        )

        # Manually create a dummy asset file to simulate a past automation run mistake
        os.makedirs(os.path.dirname(self.sandbox_file_abs), exist_ok=True)
        with open(self.sandbox_file_abs, "w") as f:
            f.write("<!-- Simulated Rogue File Content -->")

        assert os.path.exists(self.sandbox_file_abs) is True, "The file must exist before testing surgical removal metrics."

        # Dispatch a standard synchronous POST request down to our process transaction action path
        url = reverse("aurora:process_transaction_action", kwargs={"tx_id": str(tx.id)})
        response = client.post(
            url,
            data=json.dumps({"action": "DESTROY"}),
            content_type="application/json"
        )

        # Handle explicit response printouts in the case of debugging loops
        assert response.status_code == 200, f"Expected 200 but hit {response.status_code}. Details: {response.content.decode()}"
        assert response.json().get("status") == "SUCCESS"

        # Verify filesystem rollback: the rogue file must be completely wiped from disk
        assert os.path.exists(self.sandbox_file_abs) is False, "The /destroy rollback action failed to wipe the asset."

        # Verify database record state updates
        updated_tx = WorkspaceTransaction.objects.get(id=tx.id)
        assert updated_tx.status == 'ROLLED_BACK'

        self.tearDown()
# ======================================================================
# END: TRANSACTION_APPROVALS_AND_ROLLBACK_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
