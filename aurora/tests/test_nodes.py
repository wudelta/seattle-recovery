# ======================================================================
# FILE: aurora/tests/test_nodes.py (PATCH 1 OF 1)
# START: NEO4J TOPOLOGY NODES RELATIONSHIP TEST SUITE
# ======================================================================
import uuid
from django.test import TestCase
from neomodel import db
from aurora.nodes import ComponentNode

class ComponentNodeTests(TestCase):
    """Test suite ensuring Neo4j graph model property indices and dependency edges function cleanly."""

    def setUp(self):
        """Establish structural baseline identities and flush test graph space."""
        # Standard safety cleanup on the loopback connection to keep testing space pristine
        db.cypher_query("MATCH (n:ComponentNode) DETACH DELETE n")
        
        self.src_uuid = str(uuid.uuid4())
        self.dest_uuid = str(uuid.uuid4())
        
        self.src_path = "app/hopehub/pages/bed_locator.py"
        self.dest_path = "app/api/bed_locator_api.py"

    def tearDown(self):
        """Clean graph entries to avoid pipeline clutter."""
        db.cypher_query("MATCH (n:ComponentNode) DETACH DELETE n")

    def test_node_instantiation_sets_properties_accurately(self):
        """Graph Check: Verify node saves unique strings and indexing attributes securely."""
        node = ComponentNode(postgres_id=self.src_uuid, file_path=self.src_path).save()
        
        self.assertEqual(node.postgres_id, self.src_uuid)
        self.assertEqual(node.file_path, self.src_path)
        
        # Pull node back out via native neomodel index lookup matching token keys
        fetched = ComponentNode.nodes.get(postgres_id=self.src_uuid)
        self.assertEqual(fetched.file_path, self.src_path)

    def test_directed_dependency_edges_link_nodes_correctly(self):
        """Topography Check: Verify DEPENDS_ON relationships traverse directionally without leakage."""
        src_node = ComponentNode(postgres_id=self.src_uuid, file_path=self.src_path).save()
        dest_node = ComponentNode(postgres_id=self.dest_uuid, file_path=self.dest_path).save()
        
        # Connect directed dependency graph link
        src_node.depends_on.connect(dest_node)
        
        # Assert outbound parent dependency paths locate targets accurately
        all_dependencies = src_node.depends_on.all()
        self.assertEqual(len(all_dependencies), 1)
        self.assertEqual(all_dependencies[0].postgres_id, self.dest_uuid)
        
        # Assert inbound child dependency path checks traverse upstream beautifully
        all_consumers = dest_node.required_by.all()
        self.assertEqual(len(all_consumers), 1)
        self.assertEqual(all_consumers[0].postgres_id, self.src_uuid)
# ======================================================================
# END: NEO4J TOPOLOGY NODES RELATIONSHIP TEST SUITE
# ======================================================================
