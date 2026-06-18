# ======================================================================
# FILE: core_logic/tests/test_graph_client.py (PATCH 1 OF 1)
# START: CORE_LOGIC_GRAPH_TEST_SUITE
# ======================================================================
from django.test import TestCase
from app.models import ClientCase
from core_logic.utils.graph_client import Neo4jConnection

class CoreGraphTandemTestCase(TestCase):
    """
    Enforces the Transact-Graph Isolation Loop inside core_logic.
    Guarantees local graph state is cleared between testing cycles to prevent race conditions.
    """
    def setUp(self):
        # Clear relational database rows via standard test framework layers
        ClientCase.objects.all().delete()
        
        # Connect to local loopback mapping and flush graph network topology
        self.conn = Neo4jConnection()
        with self.conn.get_session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def tearDown(self):
        # Final flush execution to eliminate index collisions or dangling nodes
        with self.conn.get_session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        self.conn.close()

    def test_relational_save_triggers_graph_mirroring(self):
        """
        Verifies that saving a PostgreSQL record correctly propagates via signals to Neo4j.
        """
        # Create relational record
        case = ClientCase.objects.create(
            full_name="Alex Mercer",
            case_status="Active"
        )
        
        # Query graph network topology to confirm synchronous propagation
        query = "MATCH (c:Client {id: $client_id}) RETURN c.name AS name, c.status AS status"
        with self.conn.get_session() as session:
            result = session.run(query, client_id=str(case.id))
            record = result.single()
            
            self.assertIsNotNone(record, "Graph node was not mirrored by signal pipeline.")
            self.assertEqual(record["name"], "Alex Mercer")
            self.assertEqual(record["status"], "Active")
# ======================================================================
# END: CORE_LOGIC_GRAPH_TEST_SUITE (PATCH 1 OF 1)
# ======================================================================
