# ======================================================================
# FILE: aurora/tests/test_signals.py (PATCH 1 OF 1)
# START: NEO4J NODESET SYNTAX COMPLIANCE REALIGNMENT
# ======================================================================
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from neomodel import db
from aurora.models import ComponentRegistry
from aurora.nodes import ComponentNode

class DatabaseSignalsGraphSyncTests(TestCase):
    """Test suite ensuring real-time Postgres-to-Neo4j automated synchronization."""

    def setUp(self):
        """Establish baseline user accounts and flush test graph environments."""
        db.cypher_query("MATCH (n:ComponentNode) DETACH DELETE n")
        self.dev_user = User.objects.create_user(username="signal_tester", password="password_abc")
        self.test_path = "app/hopehub/api/realtime_sync.py"

    def tearDown(self):
        """Flush simulated graph footprints to ensure baseline isolation parameters."""
        db.cypher_query("MATCH (n:ComponentNode) DETACH DELETE n")

    def test_post_save_signal_automatically_creates_neo4j_node(self):
        """Synchronization Check: Creating a Postgres record must trigger live node creation."""
        asset = ComponentRegistry.objects.create(
            file_path=self.test_path,
            name="realtime_sync",
            created_by=self.dev_user
        )
        try:
            node = ComponentNode.nodes.get(postgres_id=str(asset.id))
            self.assertEqual(node.file_path, self.test_path)
        except ComponentNode.DoesNotExist:
            self.fail("Tandem Synchronization Fault: Neo4j node not provisioned via post_save signal.")

    def test_post_save_signal_automatically_updates_existing_neo4j_node(self):
        """Synchronization Check: Modifying a Postgres record field must replicate live changes."""
        asset = ComponentRegistry.objects.create(
            file_path=self.test_path,
            name="realtime_sync",
            created_by=self.dev_user
        )
        updated_path = "app/hopehub/api/modified_sync_route.py"
        asset.file_path = updated_path
        asset.save()

        node = ComponentNode.nodes.get(postgres_id=str(asset.id))
        self.assertEqual(node.file_path, updated_path)

    def test_post_delete_signal_cleans_up_graph_artifacts_completely(self):
        """Teardown Check: Hard erasing a database row must cleanly drop its paired graph node."""
        asset = ComponentRegistry.objects.create(
            file_path=self.test_path,
            name="realtime_sync",
            created_by=self.dev_user
        )
        postgres_id_str = str(asset.id)

        # Confirm component element exists across both layers on start
        # FIXED: Evaluates the NodeSet directly using python len() constraint verification
        self.assertGreater(len(ComponentNode.nodes.filter(postgres_id=postgres_id_str)), 0)

        # Execute deletion sequence directly on the relational tracking layer
        asset.delete()

        # Assert graph network footprint was scrubbed instantly to avoid leakage
        # FIXED: Validates that the returned NodeSet length evaluates exactly to zero
        self.assertEqual(len(ComponentNode.nodes.filter(postgres_id=postgres_id_str)), 0)
# ======================================================================
# END: NEO4J NODESET SYNTAX COMPLIANCE REALIGNMENT
# ======================================================================
